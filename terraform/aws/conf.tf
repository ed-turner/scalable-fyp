terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.54.1"
    }

    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.22.0"
    }
  }

  backend "s3" {
    bucket = "fyp-terraform-state" # assumes this bucket already exists
    key    = "terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "fyp-terraform-state-lock" # assumes this table already exists
  }
}

provider "aws" {
  region = "us-east-1"
}
