resource "aws_secretsmanager_secret" "notify_api_key" {
  name        = var.notify_api_key_secret_name
  description = var.notify_api_key_secret_description

  tags = local.tags
}
