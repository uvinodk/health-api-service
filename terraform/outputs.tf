output "ec2_public_ip" {
  value       = module.ec2.public_ip
  description = "Public IP of the EC2 instance"
}

output "health_api_url" {
  value       = "http://${module.ec2.public_ip}:8000/health"
  description = "Health API endpoint URL"
}

output "instance_id" {
  value       = module.ec2.instance_id
  description = "EC2 instance ID"
}
