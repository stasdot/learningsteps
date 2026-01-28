# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = var.tags
}

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Data source to get current client config
data "azurerm_client_config" "current" {}