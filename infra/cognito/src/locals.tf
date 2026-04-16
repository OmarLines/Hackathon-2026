locals {
  default_password_policy = {
    minimum_length                   = 8
    require_lowercase                = false
    require_numbers                  = true
    require_symbols                  = false
    require_uppercase                = false
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
