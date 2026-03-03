module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.6.0"
  name    = "${var.cluster_name}-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["${var.aws_region}a","${var.aws_region}b"]
  public_subnets  = ["10.0.1.0/24","10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24","10.0.102.0/24"]
  tags = { Environment = var.environment }
}
