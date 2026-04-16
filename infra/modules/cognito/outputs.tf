output "user_pool_arn" {
  description = "ARN of the Cognito user pool."
  value       = aws_cognito_user_pool.this.arn
}

output "user_pool_client_id" {
  description = "ID of the Cognito user pool app client."
  value       = aws_cognito_user_pool_client.this.id
}

output "user_pool_endpoint" {
  description = "Endpoint of the Cognito user pool."
  value       = aws_cognito_user_pool.this.endpoint
}

output "user_pool_id" {
  description = "ID of the Cognito user pool."
  value       = aws_cognito_user_pool.this.id
}

output "user_group_names" {
  description = "Names of Cognito user groups created by this module."
  value       = keys(aws_cognito_user_group.this)
}
