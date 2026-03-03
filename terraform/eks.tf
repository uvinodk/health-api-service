module "eks" {
  count   = var.use_apprunner ? 0 : 1
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.27"
  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.private_subnets

  node_groups = {
    default = {
      desired_capacity = var.desired_capacity
      min_capacity     = 1
      max_capacity     = 3
      instance_type    = var.node_group_instance_type
    }
  }

  tags = { Environment = var.environment }
}

output "cluster_name" {
  value = var.use_apprunner ? "" : module.eks[0].cluster_id
}
output "cluster_endpoint" {
  value = var.use_apprunner ? "" : module.eks[0].cluster_endpoint
}
output "cluster_ca_certificate" {
  value = var.use_apprunner ? "" : module.eks[0].cluster_certificate_authority_data
}
