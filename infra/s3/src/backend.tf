terraform {
  backend "s3" {
    bucket       = "hackathon-state-ctrl-atl-defeat"
    encrypt      = true
    key          = "shared/terraform.tfstate"
    region       = "eu-west-2"
    use_lockfile = true
  }
}
