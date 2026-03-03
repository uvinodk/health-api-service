variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "cluster_name" {
  type    = string
  default = "health-api-cluster"
}

variable "node_group_instance_type" {
  type    = string
  default = "t3.small"
}

variable "desired_capacity" {
  type    = number
  default = 2
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "project_name" {
  type    = string
  default = "health-api-service"
}

variable "owner" {
  type    = string
  default = "uvinodk"
}

variable "image_tag" {
  type    = string
  default = "latest"
  description = "Image tag to deploy (set by CI)."
}

variable "use_apprunner" {
  type    = bool
  default = true
  description = "If true, deploy to App Runner; otherwise use EKS."
}
