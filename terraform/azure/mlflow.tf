resource "azurerm_resource_group" "mlflow" {
  name = "org/ai/mlflow"
  location = "East US"
}

resource "azurerm_storage_account" "mlflow" {
  account_replication_type = "GRS"
  account_tier             = "Standard"
  location                 = azurerm_resource_group.mlflow.location
  name                     = "mlflow-storage"
  resource_group_name      = azurerm_resource_group.mlflow.name
}

resource "azurerm_storage_container" "mlflow" {
  name                 = "mlflow-storage-container"
  storage_account_name = azurerm_storage_account.mlflow.name
}


resource "azurerm_container_registry" "mlflow" {
  name                = "mlflow-registry"
  resource_group_name = azurerm_resource_group.mlflow.name
  location            = azurerm_resource_group.mlflow.location
  sku                 = "Premium"
  admin_enabled       = false
}

resource "azurerm_log_analytics_workspace" "mlflow" {
  name                = "mlflow-logs-01"
  location            = azurerm_resource_group.mlflow.location
  resource_group_name = azurerm_resource_group.mlflow.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "mlflow" {
  name                       = "mlflow-Environment"
  location                   = azurerm_resource_group.mlflow.location
  resource_group_name        = azurerm_resource_group.mlflow.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.mlflow.id
}

resource "azurerm_container_app" "mlflow" {
  name                         = "mlflow-app"
  container_app_environment_id = azurerm_container_app_environment.mlflow.id
  resource_group_name          = azurerm_resource_group.mlflow.name
  revision_mode                = "Single"

  template {
    container {
      name   = "mlflow"
      image  = "${azurerm_container_registry.mlflow.login_server}/:latest"
      cpu    = 0.25
      memory = "0.5Gi"
      command = [
        "mlflow",
          "server",
          "--backend-store-uri",
          "postgresql://${postgresql_role.mlflow.name}:${random_password.mlflow_db_password.result}@${module.rds.db_instance_address}:5432/fyp&options=-csearch_path%3D${postgresql_schema.mlflow.name}",
          "--default-artifact-root",
          "wasbs://${azurerm_storage_container.mlflow.name}@${azurerm_storage_account.mlflow.name}.blob.core.windows.net/fyp",
      ]
    }
  }
}

resource "aws_ecs_task_definition" "mlflow" {
    family = "mlflow"
    network_mode = "awsvpc"
    container_definitions = jsonencode([
      {
        name      = "mlflow"
        image     = "${aws_ecr_repository.mlflow.repository_url}:latest"
        memory    = 1024
        cpu       = 512
        essential = true
        portMappings = [
          {
            containerPort = 5000
            hostPort      = 5000
          }
        ]
      }
    ])
}

resource "aws_ecs_service" "mlflow" {
  name = "mlflow"
  cluster = aws_ecs_cluster.root.name
  task_definition = aws_ecs_task_definition.mlflow.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
      subnets = module.vpc.private_subnets
      security_groups = [module.vpc.default_security_group_id]
  }
  lifecycle {
    ignore_changes = [desired_count]
  }
}

resource "aws_lb" "mlflow" {
    name = "mlflow"
    internal = false
    load_balancer_type = "application"
    security_groups = [module.vpc.default_security_group_id]
    subnets = module.vpc.public_subnets
}

resource "aws_lb_target_group" "mlflow" {
    name = "mlflow"
    port = 80
    protocol = "HTTP"
    target_type = "ip"
    vpc_id = module.vpc.vpc_id
}

resource "aws_lb_listener" "mlflow" {
  load_balancer_arn = aws_lb.mlflow.arn
    port = 80
    protocol = "HTTP"
    default_action {
        type = "forward"
        target_group_arn = aws_lb_target_group.mlflow.arn
    }
}
