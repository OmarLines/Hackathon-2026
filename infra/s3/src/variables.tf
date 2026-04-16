variable "aws_region" {
  description = "AWS region where the shared Terraform state bucket will be created."
  type        = string
  default     = "eu-west-2"
}

variable "bucket_name" {
  description = "Name of the shared Terraform state bucket."
  type        = string
  default     = "hackathon-state-ctrl-atl-defeat"
}

variable "tags" {
  description = "Additional tags to apply to shared infrastructure."
  type        = map(string)
  default     = {}
}
