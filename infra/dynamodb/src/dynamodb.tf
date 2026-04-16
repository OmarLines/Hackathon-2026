resource "aws_dynamodb_table" "app" {
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = var.deletion_protection_enabled
  hash_key                    = "pk"
  name                        = var.table_name
  range_key                   = "sk"

  attribute {
    name = "gsi1pk"
    type = "S"
  }

  attribute {
    name = "gsi1sk"
    type = "S"
  }

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  global_secondary_index {
    hash_key        = "gsi1pk"
    name            = "gsi1"
    projection_type = "ALL"
    range_key       = "gsi1sk"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.tags
}
