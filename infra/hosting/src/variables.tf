variable "allowed_ingress_cidrs" {
  description = "CIDR blocks allowed to reach the public web ports."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "amazon_linux_2023_ami_ssm_parameter" {
  description = "SSM parameter used to resolve the latest Amazon Linux 2023 AMI."
  type        = string
  default     = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

variable "app_install_path" {
  description = "Base path on the instance where the app will be installed."
  type        = string
  default     = "/opt/hackathon-2026"
}

variable "app_name" {
  description = "Logical name of the hosted application."
  type        = string
  default     = "hackathon-2026-licence-app"
}

variable "app_repository_ref" {
  description = "Git ref to deploy onto the host."
  type        = string
  default     = "main"
}

variable "app_repository_url" {
  description = "Git repository to clone onto the host."
  type        = string
  default     = "https://github.com/OmarLines/Hackathon-2026.git"
}

variable "app_user" {
  description = "Linux user that will own and run the hosted application."
  type        = string
  default     = "hackathon"
}

variable "availability_zone" {
  description = "Availability Zone for the public subnet and EC2 instance. Leave null to use the first available zone."
  type        = string
  default     = null
}

variable "aws_region" {
  description = "AWS region where the hosting stack will be created."
  type        = string
  default     = "eu-west-2"
}

variable "cloudwatch_log_retention_days" {
  description = "Retention period for application and nginx log groups."
  type        = number
  default     = 30
}

variable "instance_type" {
  description = "EC2 instance type for the hosted application."
  type        = string
  default     = "t3.small"
}

variable "notify_referrer_registration_template_id" {
  description = "GOV.UK Notify template ID used for new referrer registration emails."
  type        = string
  default     = "de2d184d-7997-4c41-b45f-94e3ed208449"
}

variable "notify_referral_login_details_template_id" {
  description = "GOV.UK Notify template ID used for referred person's login details emails."
  type        = string
  default     = "83052a6e-52b4-43cd-a01a-106ea482983e"
}

variable "key_name" {
  description = "Optional EC2 key pair name. Leave null to rely on SSM Session Manager only."
  type        = string
  default     = null
}

variable "root_volume_size" {
  description = "Size in GiB of the EC2 root volume."
  type        = number
  default     = 20
}

variable "tags" {
  description = "Additional tags to apply to shared infrastructure."
  type        = map(string)
  default     = {}
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.42.0.0/24"
}

variable "vpc_cidr" {
  description = "CIDR block for the hosting VPC."
  type        = string
  default     = "10.42.0.0/16"
}
