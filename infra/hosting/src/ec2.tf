resource "aws_instance" "app" {
  ami                         = data.aws_ssm_parameter.amazon_linux_2023_ami.value
  iam_instance_profile        = aws_iam_instance_profile.app.name
  instance_type               = var.instance_type
  key_name                    = var.key_name
  monitoring                  = true
  subnet_id                   = aws_subnet.public.id
  user_data_replace_on_change = true
  vpc_security_group_ids      = [aws_security_group.app.id]

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    delete_on_termination = true
    encrypted             = true
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
  }

  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    app_directory                = local.app_directory
    app_install_path             = var.app_install_path
    app_log_directory            = local.app_log_directory
    app_log_file                 = local.app_log_file
    app_name                     = var.app_name
    app_repo_ref                 = var.app_repository_ref
    app_repo_url                 = var.app_repository_url
    app_service_name             = local.app_service_name
    app_user                     = var.app_user
    cloudwatch_agent_config_path = local.cloudwatch_agent_path
    cloudwatch_app_log_group     = aws_cloudwatch_log_group.app.name
    cloudwatch_nginx_log_group   = aws_cloudwatch_log_group.nginx.name
    nginx_server_name            = local.nginx_server_name
  })

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-app"
  })
}
