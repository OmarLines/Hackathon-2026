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
