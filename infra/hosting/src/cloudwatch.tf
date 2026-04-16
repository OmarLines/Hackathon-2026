resource "aws_cloudwatch_log_group" "app" {
  name              = "/hackathon-2026/hosting/app"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "nginx" {
  name              = "/hackathon-2026/hosting/nginx"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = local.common_tags
}
