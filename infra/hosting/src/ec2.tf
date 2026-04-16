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

  user_data = replace(templatefile("${path.module}/templates/user_data.sh.tftpl", {
    app_directory                             = local.app_directory
    app_install_path                          = var.app_install_path
    app_log_directory                         = local.app_log_directory
    app_log_file                              = local.app_log_file
    app_name                                  = var.app_name
    app_backend                               = "aws"
    app_repo_ref                              = var.app_repository_ref
    app_repo_url                              = var.app_repository_url
    app_service_name                          = local.app_service_name
    app_user                                  = var.app_user
    admin_credentials_secret_name             = data.terraform_remote_state.cognito.outputs.admin_credentials_secret_name
    aws_region                                = var.aws_region
    cognito_user_pool_client_id               = data.terraform_remote_state.cognito.outputs.cognito_user_pool_client_id
    cognito_user_pool_id                      = data.terraform_remote_state.cognito.outputs.cognito_user_pool_id
    cloudwatch_agent_config_path              = local.cloudwatch_agent_path
    cloudwatch_app_log_group                  = aws_cloudwatch_log_group.app.name
    cloudwatch_nginx_log_group                = aws_cloudwatch_log_group.nginx.name
    current_form_id                           = "children-centre-services"
    nginx_server_name                         = local.nginx_server_name
    notify_api_key_secret_name                = data.terraform_remote_state.cognito.outputs.notify_api_key_secret_name
    notify_referral_login_details_template_id = var.notify_referral_login_details_template_id
    notify_template_id                        = var.notify_referrer_registration_template_id
    referrer_details_table_name               = data.terraform_remote_state.dynamodb.outputs.referrer_details_table_name
    referrer_password_min_length              = data.terraform_remote_state.cognito.outputs.password_policy.minimum_length
    referrer_password_require_lowercase       = data.terraform_remote_state.cognito.outputs.password_policy.require_lowercase
    referrer_password_require_numbers         = data.terraform_remote_state.cognito.outputs.password_policy.require_numbers
    referrer_password_require_symbols         = data.terraform_remote_state.cognito.outputs.password_policy.require_symbols
    referrer_password_require_uppercase       = data.terraform_remote_state.cognito.outputs.password_policy.require_uppercase
    referrals_table_name                      = data.terraform_remote_state.dynamodb.outputs.table_name
  }), "\r\n", "\n")

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-app"
  })
}
