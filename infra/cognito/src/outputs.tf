output "cognito_user_group_names" {
  description = "Cognito groups created for coarse roles."
  value       = module.cognito_user_pool.user_group_names
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito user pool."
  value       = module.cognito_user_pool.user_pool_arn
}

output "cognito_user_pool_client_id" {
  description = "App client ID for the licence application."
  value       = module.cognito_user_pool.user_pool_client_id
}

output "cognito_user_pool_endpoint" {
  description = "Endpoint of the Cognito user pool."
  value       = module.cognito_user_pool.user_pool_endpoint
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito user pool."
  value       = module.cognito_user_pool.user_pool_id
}

output "notify_api_key_secret_arn" {
  description = "ARN of the GOV Notify API key secret."
  value       = aws_secretsmanager_secret.notify_api_key.arn
}

output "notify_api_key_secret_name" {
  description = "Name of the GOV Notify API key secret."
  value       = aws_secretsmanager_secret.notify_api_key.name
}

output "admin_credentials_secret_arn" {
  description = "ARN of the admin username and password secret."
  value       = aws_secretsmanager_secret.admin_credentials.arn
}

output "admin_credentials_secret_name" {
  description = "Name of the admin username and password secret."
  value       = aws_secretsmanager_secret.admin_credentials.name
}

output "password_policy" {
  description = "Password policy used by the Cognito user pool."
  value       = local.default_password_policy
}
