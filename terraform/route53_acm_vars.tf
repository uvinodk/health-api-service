variable "domain_name" {
  type        = string
  description = "Domain name for Route53 record (e.g., health-api.example.com)"
  default     = ""
}

variable "route53_zone_id" {
  type        = string
  description = "Route53 hosted zone ID for creating DNS record"
  default     = ""
}

variable "enable_https" {
  type        = bool
  description = "Enable HTTPS with ACM certificate"
  default     = false
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS (required if enable_https=true)"
  default     = ""
}
