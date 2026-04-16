locals {
  app_directory         = "${var.app_install_path}/current"
  app_log_directory     = "/var/log/${var.app_name}"
  app_log_file          = "${local.app_log_directory}/app.log"
  app_service_name      = var.app_name
  cloudwatch_agent_path = "/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json"
  nginx_server_name     = "_"

  common_tags = merge(
    {
      component  = "hosting"
      managed_by = "terraform"
      project    = "hackathon-2026"
      repo       = "Hackathon-2026"
    },
    var.tags
  )

  selected_availability_zone = coalesce(var.availability_zone, data.aws_availability_zones.available.names[0])
}
