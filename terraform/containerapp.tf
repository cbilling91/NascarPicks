resource "azurerm_resource_group" "nascar_rg" {
  name     = "rg-nascar-terraform"
  location = "eastus"
}

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



resource "azurerm_container_app" "nascar_aca" {
  name                         = "nascar-frontend-demo"
  container_app_environment_id = azurerm_container_app_environment.nascar_aca_environment.id
  resource_group_name          = azurerm_resource_group.nascar_rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "helloworld-app"
      image  = "ghcr.io/cbilling91/nascar-picks/front-end:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
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

  secret {
    name = azurerm_cosmosdb_account.nascar_db_account.name
    value = azurerm_cosmosdb_account.nascar_db_account.primary_key
  }

  dapr {
    app_id = "nascarpicks"
  }
}

resource "azurerm_container_app_environment_dapr_component" "output" {
  name                         = "nascar-db"
  container_app_environment_id = azurerm_container_app_environment.nascar_aca_environment.id
  component_type               = "bindings.azure.cosmosdb"
  version                      = "v1"

  secret {
    name = azurerm_cosmosdb_account.nascar_db_account.name
    value = azurerm_cosmosdb_account.nascar_db_account.primary_key
  }
  
  metadata {
    name  = "url"
    value = azurerm_cosmosdb_account.nascar_db_account.endpoint
  }

  metadata {
    name  = "masterKey"
    secret_name = azurerm_cosmosdb_account.nascar_db_account.name
  }

  metadata {
    name  = "database"
    value = azurerm_cosmosdb_sql_database.nascar_db.name
  }

  metadata {
    name  = "collection"
    value = azurerm_cosmosdb_sql_container.nascar_db_collection.name
  }
}

output "app_url" {
  value = azurerm_container_app.nascar_aca.latest_revision_fqdn
}