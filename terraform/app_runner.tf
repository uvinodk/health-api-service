resource "aws_iam_role" "apprunner_access" {
  name = "apprunner-access-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "apprunner_access_policy" {
  name = "apprunner-access-policy"
  role = aws_iam_role.apprunner_access.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_apprunner_service" "app" {
  count        = var.use_apprunner ? 1 : 0
  service_name = "health-api-apprunner"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"
      image_configuration {
        port = "8000"
      }
    }
  }

  instance_configuration {
    cpu    = "1024"
    memory = "2048"
  }

  tags = { Environment = var.environment }
}

output "apprunner_service_arn" {
  value = var.use_apprunner ? aws_apprunner_service.app[0].arn : ""
  description = "ARN of the App Runner service (if used)"
}

output "apprunner_service_url" {
  value = var.use_apprunner ? aws_apprunner_service.app[0].service_url : ""
  description = "URL of the App Runner service"
}
