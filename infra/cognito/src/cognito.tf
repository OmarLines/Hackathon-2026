module "cognito_user_pool" {
  source = "../../modules/cognito"

  deletion_protection   = var.deletion_protection
  password_policy       = local.default_password_policy
  tags                  = local.tags
  user_groups           = var.user_groups
  user_pool_client_name = var.user_pool_client_name
  user_pool_name        = var.user_pool_name
}
