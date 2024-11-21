resource "aws_ecr_repository" "mlflow" {
  name = "org/ai/mlflow"
}

resource "aws_s3_bucket" "mlflow" {
    bucket = "mlflow-registry"
}

resource "aws_ecs_task_definition" "mlflow" {
    family = "mlflow"

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
        command = [
          "mlflow",
          "server",
          "--backend-store-uri",
          "postgresql://${postgresql_role.mlflow.name}:${random_password.mlflow_db_password.result}@${module.rds.db_instance_address}:5432/fyp&options=-csearch_path%3D${postgresql_schema.mlflow.name}",
          "--default-artifact-root",
          "s3://${aws_s3_bucket.mlflow.bucket}/fyp",
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
