terraform {
  required_version = ">= 1.3"
  required_providers {
    aws = { source = "hashicorp/aws" version = "~> 5.0" }
  }
  backend "s3" {
    bucket         = "REPLACE_TFSTATE_BUCKET"
    key            = "health-api-service/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = "REPLACE_TFSTATE_LOCK_TABLE"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
