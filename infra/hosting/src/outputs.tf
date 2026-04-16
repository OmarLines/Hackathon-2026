output "app_clone_source" {
  description = "Repository and ref configured for the instance bootstrap."
  value = {
    ref = var.app_repository_ref
    url = var.app_repository_url
  }
}

output "elastic_ip" {
  description = "Elastic IP attached to the application instance."
  value       = aws_eip.app.public_ip
}

output "instance_id" {
  description = "ID of the application instance."
  value       = aws_instance.app.id
}

output "instance_ssm_target" {
  description = "Instance ID used as the SSM Session Manager target."
  value       = aws_instance.app.id
}

output "public_http_url" {
  description = "Public HTTP URL for the hosted application."
  value       = "http://${aws_eip.app.public_ip}"
}

output "public_subnet_id" {
  description = "Public subnet hosting the application instance."
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Security group attached to the application instance."
  value       = aws_security_group.app.id
}

output "vpc_id" {
  description = "Hosting VPC ID."
  value       = aws_vpc.hosting.id
}
