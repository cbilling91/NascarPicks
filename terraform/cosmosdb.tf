resource "azurerm_cosmosdb_account" "nascar_db_account" {
  name                = "nascar-picks-cosmosdb-account"
  resource_group_name = azurerm_resource_group.nascar_rg.name
  location            = azurerm_resource_group.nascar_rg.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix   = 100
  }

  geo_location {
    location          = "East US"  # Replace with your desired region
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "nascar_db" {
  name                = "nascar-database"
  resource_group_name = azurerm_resource_group.nascar_rg.name
  account_name        = azurerm_cosmosdb_account.nascar_db_account.name
  autoscale_settings {
    max_throughput = 1000
  }
}

resource "azurerm_cosmosdb_sql_container" "nascar_db_collection" {
  name                = "nascar-collection"
  resource_group_name = azurerm_resource_group.nascar_rg.name
  account_name        = azurerm_cosmosdb_account.nascar_db_account.name
  database_name       = azurerm_cosmosdb_sql_database.nascar_db.name
  partition_key_path    = "/partitionKey"
  partition_key_version = 1
  autoscale_settings {
    max_throughput = 1000
  }
}