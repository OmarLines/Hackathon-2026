variable "aws_region" {
  description = "AWS region where the DynamoDB table will be created."
  type        = string
  default     = "eu-west-2"
}

variable "deletion_protection_enabled" {
  description = "Enable deletion protection on the DynamoDB table."
  type        = bool
  default     = true
}

variable "table_name" {
  description = "Name of the DynamoDB table for referrer profiles, access, and referrals."
  type        = string
  default     = "hackathon-2026-app-data"
}

variable "tags" {
  description = "Additional tags to apply to shared infrastructure."
  type        = map(string)
  default     = {}
}
