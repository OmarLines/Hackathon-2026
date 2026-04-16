variable "aws_region" {
  description = "AWS region where the Cognito resources will be created."
  type        = string
  default     = "eu-west-2"
}

variable "deletion_protection" {
  description = "Deletion protection mode for the user pool."
  type        = string
  default     = "INACTIVE"
}

variable "tags" {
  description = "Additional tags to apply to shared infrastructure."
  type        = map(string)
  default     = {}
}

variable "user_groups" {
  description = "Optional coarse-grained Cognito groups. Per-form access should be stored separately."
  type = list(object({
    name        = string
    description = optional(string)
    precedence  = optional(number)
    role_arn    = optional(string)
  }))
  default = []
}

variable "user_pool_client_name" {
  description = "Name of the Cognito app client for the licence application service."
  type        = string
  default     = "hackathon-2026-licence-app-web"
}

variable "user_pool_name" {
  description = "Name of the Cognito user pool for the licence application service."
  type        = string
  default     = "hackathon-2026-app-users"
}

variable "notify_api_key_secret_description" {
  description = "Description for the GOV Notify API key secret."
  type        = string
  default     = "GOV Notify API key for Hackathon 2026 referrer account emails."
}

variable "notify_api_key_secret_name" {
  description = "Secrets Manager name for the GOV Notify API key."
  type        = string
  default     = "hackathon-2026-notify_api_key"
}

variable "admin_credentials_secret_description" {
  description = "Description for the admin username and password secret."
  type        = string
  default     = "Admin username and password for Hackathon 2026."
}

variable "admin_credentials_secret_name" {
  description = "Secrets Manager name for the admin username and password secret."
  type        = string
  default     = "hackathon-2026-admin_credentials"
}
