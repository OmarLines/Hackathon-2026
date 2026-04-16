variable "deletion_protection" {
  description = "Deletion protection mode for the user pool."
  type        = string
  default     = "INACTIVE"
}

variable "explicit_auth_flows" {
  description = "Explicit auth flows enabled for the app client."
  type        = list(string)
  default = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]
}

variable "password_policy" {
  description = "Password policy for the user pool."
  type = object({
    minimum_length                   = number
    require_lowercase                = bool
    require_numbers                  = bool
    require_symbols                  = bool
    require_uppercase                = bool
    temporary_password_validity_days = number
  })
}

variable "tags" {
  description = "Tags to apply to Cognito resources."
  type        = map(string)
  default     = {}
}

variable "user_groups" {
  description = "Optional Cognito groups for coarse roles. Form-level access should live elsewhere."
  type = list(object({
    name        = string
    description = optional(string)
    precedence  = optional(number)
    role_arn    = optional(string)
  }))
  default = []
}

variable "user_pool_client_name" {
  description = "Name of the Cognito user pool app client."
  type        = string
}

variable "user_pool_name" {
  description = "Name of the Cognito user pool."
  type        = string
}
