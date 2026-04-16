output "table_arn" {
  description = "ARN of the DynamoDB application table."
  value       = aws_dynamodb_table.app.arn
}

output "table_name" {
  description = "Name of the DynamoDB application table."
  value       = aws_dynamodb_table.app.name
}
