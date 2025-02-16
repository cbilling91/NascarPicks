resource "azurerm_log_analytics_workspace" "nascar_workspace" {
  name                = "nascar-workspace-aca"
  location            = azurerm_resource_group.nascar_rg.location
  resource_group_name = azurerm_resource_group.nascar_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "nascar_aca_environment" {
  name                       = "nascar-aca-environment"
  location                   = azurerm_resource_group.nascar_rg.location
  resource_group_name        = azurerm_resource_group.nascar_rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.nascar_workspace.id

}

resource "azurerm_container_app_environment_dapr_component" "cockroach_db" {
  name                         = "nascar-cockroach-statestore"
  container_app_environment_id = azurerm_container_app_environment.nascar_aca_environment.id
  component_type               = "state.cockroachdb"
  version                      = "v1"
  scopes = azurerm_container_app.nascar_aca.dapr[*].app_id

  secret {
    name = "cockroach-db-connection-string"
    value = var.cockroach_db_connection_string
  }

  metadata {
    name  = "connectionString"
    secret_name = "cockroach-db-connection-string"
  }
}

resource "azurerm_container_app" "nascar_aca" {
  name                         = "nascar-frontend-demo"
  container_app_environment_id = azurerm_container_app_environment.nascar_aca_environment.id
  resource_group_name          = azurerm_resource_group.nascar_rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "helloworld-app"
      image  = "ghcr.io/cbilling91/nascar-picks/front-end:047689b4"
      cpu    = 0.25
      memory = "0.5Gi"
    }
    min_replicas = 1
    #revision_suffix = "nascarpicks-v5"
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8000
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  dapr {
    app_id = "nascarpicks"
  }
}

resource "azurerm_container_app_job" "nascar_aca_notifications" {
  name                         = "nascar-pick-notifications"
  location                     = azurerm_resource_group.nascar_rg.location
  container_app_environment_id = azurerm_container_app_environment.nascar_aca_environment.id
  resource_group_name          = azurerm_resource_group.nascar_rg.name

  replica_timeout_in_seconds = 60

  template {
    container {
      name   = "nascar-notifications"
      image  = "ghcr.io/cbilling91/nascar-picks/notifications:047689b4"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name = "CONNECTION_STRING"
        secret_name = "cockroach-db-connection-string"
      }

      env {
        name = "TWILIO_ACCOUNT_SID"
        secret_name = "nascar-picks-twilio-account-sid"
      }

      env {
        name = "TWILIO_AUTH_TOKEN"
        secret_name = "nascar-picks-twilio-auth-token"
      }
    }
  }

  secrets {
    name = "cockroach-db-connection-string"
    value = var.cockroach_db_connection_string
  }

  secrets {
    name = "nascar-picks-twilio-account-sid"
    value = var.twilio_account_sid
  }

  secrets {
    name = "nascar-picks-twilio-auth-token"
    value = var.twilio_auth_token
  }

  schedule_trigger_config {
    cron_expression = "0 16 * * 6"
  }
}

output "app_url" {
  value = "https://${azurerm_container_app.nascar_aca.latest_revision_fqdn}"
}