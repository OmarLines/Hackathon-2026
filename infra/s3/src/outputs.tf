output "terraform_state_backend" {
  description = "Suggested backend configuration for future Terraform stacks."
  value = {
    bucket       = module.terraform_state_bucket.bucket_name
    encrypt      = true
    key          = "shared/terraform.tfstate"
    region       = var.aws_region
    use_lockfile = true
  }
}

output "terraform_state_bucket_arn" {
  description = "ARN of the shared Terraform state bucket."
  value       = module.terraform_state_bucket.bucket_arn
}

output "terraform_state_bucket_name" {
  description = "Name of the shared Terraform state bucket."
  value       = module.terraform_state_bucket.bucket_name
}
