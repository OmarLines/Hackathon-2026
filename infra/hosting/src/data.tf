data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ssm_parameter" "amazon_linux_2023_ami" {
  name = var.amazon_linux_2023_ami_ssm_parameter
}

data "terraform_remote_state" "cognito" {
  backend = "s3"

  config = {
    bucket = "hackathon-state-ctrl-atl-defeat"
    key    = "cognito/terraform.tfstate"
    region = var.aws_region
  }
}

data "terraform_remote_state" "dynamodb" {
  backend = "s3"

  config = {
    bucket = "hackathon-state-ctrl-atl-defeat"
    key    = "dynamodb/terraform.tfstate"
    region = var.aws_region
  }
}
