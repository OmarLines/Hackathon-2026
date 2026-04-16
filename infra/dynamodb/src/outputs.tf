output "table_arn" {
  description = "ARN of the DynamoDB application table."
  value       = aws_dynamodb_table.app.arn
}

output "table_name" {
  description = "Name of the DynamoDB application table."
  value       = aws_dynamodb_table.app.name
}

output "referrer_details_table_arn" {
  description = "ARN of the DynamoDB table for saved referrer step defaults."
  value       = aws_dynamodb_table.referrer_details.arn
}

output "referrer_details_table_name" {
  description = "Name of the DynamoDB table for saved referrer step defaults."
  value       = aws_dynamodb_table.referrer_details.name
}
