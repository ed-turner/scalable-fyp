
resource "aws_ecr_repository" "job" {
  name = "/org/ai/fyp"
}

resource "aws_cloudwatch_log_group" "job" {
  name = "/org/ai/fyp"
}

resource "aws_ecs_task_definition" "job" {
  family                = "fyp-job"
  network_mode          = "awsvpc"
  cpu                   = 256
  memory                = 512
  requires_compatibilities = ["FARGATE"]
  execution_role_arn     = aws_iam_role.execution_role.arn
  task_role_arn          = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    {
      name      = "job"
      image     = "${aws_ecr_repository.job.repository_url}:latest"
      memory    = 512
      cpu       = 256
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ]
      environment = [
        {
          name  = "MLFLOW_TRACKING_URI"
          value = aws_lb.mlflow.dns_name
        }
      ]
    }
  ])

}
