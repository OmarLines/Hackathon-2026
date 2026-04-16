locals {
  default_tags = {
    component  = "data"
    managed_by = "terraform"
    project    = "hackathon-2026"
    repo       = "Hackathon-2026"
  }

  tags = merge(local.default_tags, var.tags)
}
