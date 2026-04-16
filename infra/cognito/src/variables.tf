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
