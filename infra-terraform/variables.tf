variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "learningsteps-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "learningsteps"
}

# Network Configuration
variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "aks_subnet_prefix" {
  description = "Address prefix for AKS subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "database_subnet_prefix" {
  description = "Address prefix for database subnet"
  type        = string
  default     = "10.0.2.0/24"
}

# AKS Configuration
variable "aks_node_count" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 2
}

variable "aks_node_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2_v3" # Cost-effective for development
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = null # Update to latest stable version
}

# Database Configuration
variable "db_admin_username" {
  description = "Database administrator username"
  type        = string
  default     = "learningsteps"
}

variable "db_sku_name" {
  description = "Database SKU"
  type        = string
  default     = "B_Standard_B1ms" # Burstable tier for cost savings
}

variable "db_storage_mb" {
  description = "Database storage in MB"
  type        = number
  default     = 32768 # 32 GB
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}

# ACR Configuration
variable "acr_name" {
  description = "Name of the Azure Container Registry"
  type        = string
  default     = "learningstepsacr"
}

variable "acr_sku" {
  description = "SKU for Azure Container Registry"
  type        = string
  default     = "Basic"
}

# Key Vault Configuration
variable "keyvault_name" {
  description = "Name of the Key Vault"
  type        = string
  default     = "learningsteps-kv"
}

# Application Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "api.learningsteps.cloud"
}

# Tags
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "LearningSteps"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}