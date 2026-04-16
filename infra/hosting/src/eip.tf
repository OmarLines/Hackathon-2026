resource "aws_eip" "app" {
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-app"
  })
}

resource "aws_eip_association" "app" {
  allocation_id = aws_eip.app.id
  instance_id   = aws_instance.app.id
}
