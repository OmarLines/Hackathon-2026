resource "aws_secretsmanager_secret" "notify_api_key" {
  name        = var.notify_api_key_secret_name
  description = var.notify_api_key_secret_description

  tags = local.tags
}

resource "aws_secretsmanager_secret" "admin_credentials" {
  name        = var.admin_credentials_secret_name
  description = var.admin_credentials_secret_description

  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "admin_credentials" {
  secret_id = aws_secretsmanager_secret.admin_credentials.id
  secret_string = jsonencode({
    username = "admin"
    password = "admin"
  })
}
