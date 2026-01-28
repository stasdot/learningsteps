########################################
# PostgreSQL Flexible Server (private)
########################################

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location

  version                = var.postgres_version
  sku_name               = var.db_sku_name
  storage_mb             = var.db_storage_mb

  administrator_login    = var.db_admin_username
  administrator_password = random_password.db_password.result

  delegated_subnet_id = azurerm_subnet.database.id
  private_dns_zone_id = azurerm_private_dns_zone.postgres.id
  public_network_access_enabled = false


  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  

  tags = var.tags

  lifecycle {
    ignore_changes = [
      zone
    ]
  }

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.postgres
  ]
}

########################################
# Database
########################################

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "learningsteps"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

########################################
# PostgreSQL Extensions
########################################

resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "uuid-ossp,pgcrypto"
}

########################################
# Store DB secrets in Key Vault
########################################

resource "azurerm_key_vault_secret" "db_host" {
  name         = "database-host"
  value        = azurerm_postgresql_flexible_server.main.fqdn
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "db_username" {
  name         = "database-username"
  value        = var.db_admin_username
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "database-password"
  value        = random_password.db_password.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "db_name" {
  name         = "database-name"
  value        = azurerm_postgresql_flexible_server_database.main.name
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "database_url" {
  name  = "database-url"
  value = "postgresql://${var.db_admin_username}:${random_password.db_password.result}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.main.name}?sslmode=require"

  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}
