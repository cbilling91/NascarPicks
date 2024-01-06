provider "azurerm" {
  features = {}
}

resource "azurerm_resource_group" "example" {
  name     = "example-resource-group"
  location = "East US"
}

resource "azurerm_container_group" "example" {
  name                = "example-container-group"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  os_type       = "Linux"
  restart_policy = "Always"

  container {
    name   = "example-container"
    image  = "nginx:latest"
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 80
      protocol = "TCP"
    }
  }
}

resource "azurerm_application_gateway" "example" {
  name                = "example-app-gateway"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  sku {
    name     = "Standard_Small"
    tier     = "Standard"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "example-gateway-ip-configuration"
    subnet_id = azurerm_container_group.example.ip_address[0].subnet_id
  }

  frontend_port {
    name = "example-frontend-port"
    port = 80
  }

  frontend_ip_configuration {
    name                 = "example-frontend-ip-configuration"
    public_ip_address_id = azurerm_container_group.example.ip_address[0].id
  }

  http_listener {
    name                           = "example-http-listener"
    frontend_ip_configuration_name = azurerm_application_gateway.example.frontend_ip_configuration[0].name
    frontend_port_name             = azurerm_application_gateway.example.frontend_port[0].name
  }

  request_routing_rule {
    name                       = "example-request-routing-rule"
    rule_type                  = "PathBasedRouting"
    http_listener_name         = azurerm_application_gateway.example.http_listener[0].name
    backend_address_pool_name  = azurerm_container_group.example.backend_address_pool[0].name
    backend_http_settings_name = azurerm_container_group.example.http_settings[0].name
  }

  backend_address_pool {
    name = "example-backend-address-pool"
  }

  backend_http_settings {
    name                  = "example-backend-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
  }
}
