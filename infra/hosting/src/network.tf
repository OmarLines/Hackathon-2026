resource "aws_vpc" "hosting" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-vpc"
  })
}

resource "aws_internet_gateway" "hosting" {
  vpc_id = aws_vpc.hosting.id

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-igw"
  })
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.hosting.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = local.selected_availability_zone
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-public"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.hosting.id

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-public"
  })
}

resource "aws_route" "internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.hosting.id
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
