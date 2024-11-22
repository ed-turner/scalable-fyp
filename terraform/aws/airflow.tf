
resource "aws_s3_bucket" "root" {
  bucket = "ai-root"
}

resource "aws_mwaa_environment" "root" {
  dag_s3_path        = "dags/"
  execution_role_arn = aws_iam_role.execution_role.arn
  name               = "org-ai-root"

  network_configuration {
    security_group_ids = [module.vpc.default_security_group_id]
    subnet_ids         = module.vpc.private_subnets
  }

  source_bucket_arn = aws_s3_bucket.root.arn

  tags = {
    Name        = "fyp"
    Environment = "production"
  }

}
