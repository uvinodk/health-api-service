data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "github_actions" {
  name = "github-actions-health-api-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Federated = data.aws_iam_openid_connect_provider.github.arn },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:uvinodk/health-api-service:*"
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

resource "aws_iam_role_policy" "github_actions_policy" {
  role = aws_iam_role.github_actions.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ],
        Resource = aws_ecr_repository.app.arn
      },
      {
        Effect = "Allow",
        Action = [
          "apprunner:CreateService",
          "apprunner:DeleteService",
          "apprunner:DescribeService",
          "apprunner:StartDeployment",
          "apprunner:PauseService",
          "apprunner:ResumeService",
          "apprunner:ListServices"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:PassRole",
          "iam:AttachRolePolicy",
          "iam:PutRolePolicy",
          "iam:GetRole"
        ],
        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/health-api-*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "route53:ChangeResourceRecordSets"
        ],
        Resource = "arn:aws:route53::${data.aws_caller_identity.current.account_id}:hostedzone/*"
      },
      {
        Effect = "Allow",
        Action = [
          "acm:RequestCertificate",
          "acm:DescribeCertificate",
          "acm:ListCertificates"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "eks:DescribeCluster"
        ],
        Resource = var.use_apprunner ? "*" : module.eks[0].cluster_arn
      }
    ]
  })
}

output "github_oidc_role_arn" { value = aws_iam_role.github_actions.arn }
