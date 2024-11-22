

resource "aws_ssm_parameter" "ecs_cluster" {
  name = "/fyp/ecs/cluster_name"
  type = "String"
  value = aws_ecs_cluster.root.name
}

resource "aws_ssm_parameter" "vpc_id" {
  name = "/fyp/vpc/vpc_id"
  type = "String"
  value = module.vpc.vpc_id
}

resource "aws_ssm_parameter" "vpc_private_subnets" {
  name = "/fyp/vpc/private_subnets"
  type = "String"
  value = jsonencode(module.vpc.private_subnets)
}

resource "aws_ssm_parameter" "vpc_public_subnets" {
  name = "/fyp/vpc/public_subnets"
  type = "String"
  value = jsonencode(module.vpc.public_subnets)
}

resource "aws_ssm_parameter" "vpc_default_security_group_id" {
  name = "/fyp/vpc/default_security_group_id"
  type = "String"
  value = module.vpc.default_security_group_id
}

resource "aws_ssm_parameter" "fyp_task_definition" {
  name = "/fyp/ecs/task_definition"
  type = "String"
  value = aws_ecs_task_definition.job.arn
}

resource "aws_ssm_parameter" "fyp_log_group" {
  name = "/fyp/ecs/log_group"
  type = "String"
  value = aws_cloudwatch_log_group.job.name
}