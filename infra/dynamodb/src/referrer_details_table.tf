resource "aws_dynamodb_table" "referrer_details" {
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = var.deletion_protection_enabled
  hash_key                    = "user_id"
  name                        = var.referrer_details_table_name

  attribute {
    name = "user_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.tags
}
