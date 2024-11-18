
resource "random_password" "primary_db_password" {
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


