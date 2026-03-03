resource "aws_ecr_repository" "app" {
  name                 = "health-api-service"
  image_tag_mutability = "MUTABLE"
  tags = {
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
