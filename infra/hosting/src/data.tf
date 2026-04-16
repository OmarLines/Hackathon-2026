data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ssm_parameter" "amazon_linux_2023_ami" {
  name = var.amazon_linux_2023_ami_ssm_parameter
}
