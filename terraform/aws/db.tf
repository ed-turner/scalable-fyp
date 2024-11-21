
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


module "rds" {
  source  = "terraform-aws-modules/rds/aws"

  identifier          = "fyp"

  engine = "postgres"
  engine_version = "14"
  family = "postgres14"

  major_engine_version = "14"
  instance_class = "db.t4g.large"

  allocated_storage = 20
  max_allocated_storage = 100

  username        = "admin"
  db_name = "fyp"
  port = 5432

  manage_master_user_password = false
  manage_master_user_password_rotation = false
  password        = random_password.primary_db_password.result

  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    }
  ]

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  create_monitoring_role                = true
  monitoring_interval                   = 60
  monitoring_role_name                  = "fyp-monitoring-role-name"
  monitoring_role_use_name_prefix       = true
  monitoring_role_description           = "Description for fyp monitoring role"

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}


provider "postgresql" {
  host     = module.rds.db_instance_address
  port     = 5432
  password = random_password.primary_db_password.result
  sslmode = "require"
  username = "admin"
}

resource "postgresql_database" "root" {
  name = "fyp"
}

resource "postgresql_role" "mlflow" {
  name = "mlflow"
  login = true
  password = random_password.mlflow_db_password.result
}

resource "postgresql_role" "job" {
  name = "job"
  login = true
  password = random_password.job_db_password.result
}

resource "postgresql_schema" "mlflow" {
  name = "mlflow"
  owner = postgresql_role.mlflow.name
}

resource "postgresql_schema" "job" {
  name = "RANKING_FEATURES"
  owner = postgresql_role.job.name
}

resource "postgresql_grant" "mlflow" {
  database = postgresql_database.root.name
  schema = postgresql_schema.mlflow.name
  role = postgresql_role.mlflow.name
  privileges = ["ALL"]
  object_type = "schema"
}

resource "postgresql_grant" "job_public" {
    database = postgresql_database.root.name
    schema = "public"
    role = postgresql_role.job.name
    privileges = ["SELECT"]
    object_type = "schema"
}


resource "postgresql_grant" "job_internal" {
    database = postgresql_database.root.name
    schema = postgresql_schema.job.name
    role = postgresql_role.job.name
    privileges = ["ALL"]
    object_type = "schema"
}