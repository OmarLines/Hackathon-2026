resource "aws_cognito_user_pool" "this" {
  name                     = var.user_pool_name
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]
  deletion_protection      = var.deletion_protection

  username_configuration {
    case_sensitive = false
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  password_policy {
    minimum_length                   = var.password_policy.minimum_length
    require_lowercase                = var.password_policy.require_lowercase
    require_numbers                  = var.password_policy.require_numbers
    require_symbols                  = var.password_policy.require_symbols
    require_uppercase                = var.password_policy.require_uppercase
    temporary_password_validity_days = var.password_policy.temporary_password_validity_days
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  schema {
    attribute_data_type = "String"
    mutable             = true
    name                = "email"
    required            = true

    string_attribute_constraints {
      min_length = 5
      max_length = 256
    }
  }

  tags = var.tags
}

resource "aws_cognito_user_pool_client" "this" {
  name         = var.user_pool_client_name
  user_pool_id = aws_cognito_user_pool.this.id

  access_token_validity                = 60
  auth_session_validity                = 3
  enable_token_revocation              = true
  explicit_auth_flows                  = var.explicit_auth_flows
  generate_secret                      = false
  id_token_validity                    = 60
  prevent_user_existence_errors        = "ENABLED"
  read_attributes                      = ["email", "email_verified"]
  refresh_token_validity               = 30
  write_attributes                     = ["email"]
  allowed_oauth_flows_user_pool_client = false

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}

resource "aws_cognito_user_group" "this" {
  for_each = {
    for group in var.user_groups : group.name => group
  }

  name         = each.value.name
  description  = try(each.value.description, null)
  precedence   = try(each.value.precedence, null)
  role_arn     = try(each.value.role_arn, null)
  user_pool_id = aws_cognito_user_pool.this.id
}
