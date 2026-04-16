module "terraform_state_bucket" {
  source = "../../modules/s3"

  bucket_name = var.bucket_name
  tags        = local.tags
}
