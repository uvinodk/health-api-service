# ACM Certificate Configuration (optional)

# If using an existing ACM certificate, set the ARN
# data "aws_acm_certificate" "existing" {
#   domain   = var.domain_name
#   statuses = ["ISSUED"]
# }

# For automatic certificate creation, use the following:
# resource "aws_acm_certificate" "app" {
#   count             = var.enable_https && var.acm_certificate_arn == "" ? 1 : 0
#   domain_name       = var.domain_name
#   validation_method = "DNS"
#   tags              = { Environment = var.environment }
#
#   lifecycle {
#     create_before_destroy = true
#   }
# }

# Note: ACM certificate validation via DNS would require Route53 integration
# For now, use an existing certificate ARN or issue manually in AWS console
