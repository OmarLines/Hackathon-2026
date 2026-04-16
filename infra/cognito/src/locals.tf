locals {
  default_password_policy = {
    minimum_length                   = 14
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  default_tags = {
    component  = "identity"
    managed_by = "terraform"
    project    = "hackathon-2026"
    repo       = "Hackathon-2026"
  }

  tags = merge(local.default_tags, var.tags)
}
