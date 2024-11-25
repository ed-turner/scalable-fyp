terraform {
  required_providers {
    mssql = {
      source  = "saritasa-nest/mssql"
      version = "0.0.4"
    }
    mssql = {
      source  = "saritasa-nest/mssql"
      version = "0.0.4"
    }
    mssql = {
      source  = "saritasa-nest/mssql"
      version = "0.0.4"
    }
  }
}
resource "random_password" "primary_db_password" {
  length = 16
  special = true
}


resource "random_password" "mlflow_db_password" {
  length = 16
  special = true
}


resource "random_password" "job_db_password" {
  length = 16
  special = true
}


resource "azurerm_mssql_server" "mlflow" {
  name                         = "mlflow-sqlserver"
  resource_group_name          = azurerm_resource_group.mlflow.name
  location                     = azurerm_resource_group.mlflow.location
  version                      = "12.0"
  administrator_login          = "admin"
  administrator_login_password = random_password.primary_db_password.result
}

resource "azurerm_mssql_database" "mlflow" {
  name         = "example-db"
  server_id    = azurerm_mssql_server.mlflow.id
  collation    = "SQL_Latin1_General_CP1_CI_AS"
  license_type = "LicenseIncluded"
  max_size_gb  = 2
  sku_name     = "S0"
  enclave_type = "VBS"

  tags = {
    foo = "bar"
  }

  # prevent the possibility of accidental data loss
  lifecycle {
    prevent_destroy = true
  }
}


provider "mssql" {
}
#
# resource "postgresql_database" "root" {
#   name = "fyp"
# }
#
# resource "postgresql_role" "mlflow" {
#   name = "mlflow"
#   login = true
#   password = random_password.mlflow_db_password.result
# }
#
# resource "postgresql_role" "job" {
#   name = "job"
#   login = true
#   password = random_password.job_db_password.result
# }
#
# resource "postgresql_schema" "mlflow" {
#   name = "mlflow"
#   owner = postgresql_role.mlflow.name
# }
#
# resource "postgresql_schema" "job" {
#   name = "RANKING_FEATURES"
#   owner = postgresql_role.job.name
# }
#
# resource "postgresql_grant" "mlflow" {
#   database = postgresql_database.root.name
#   schema = postgresql_schema.mlflow.name
#   role = postgresql_role.mlflow.name
#   privileges = ["ALL"]
#   object_type = "schema"
# }
#
# resource "postgresql_grant" "job_public" {
#     database = postgresql_database.root.name
#     schema = "public"
#     role = postgresql_role.job.name
#     privileges = ["SELECT"]
#     object_type = "schema"
# }
#
#
# resource "postgresql_grant" "job_internal" {
#     database = postgresql_database.root.name
#     schema = postgresql_schema.job.name
#     role = postgresql_role.job.name
#     privileges = ["ALL"]
#     object_type = "schema"
# }