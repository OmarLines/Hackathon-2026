data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  name               = "hackathon-2026-hosting-ec2"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(local.common_tags, {
    Name = "hackathon-2026-hosting-ec2"
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

data "aws_iam_policy_document" "app_backend_access" {
  statement {
    actions = [
      "cognito-idp:AdminCreateUser",
      "cognito-idp:AdminDeleteUser",
      "cognito-idp:AdminSetUserPassword",
      "cognito-idp:ListUsers",
    ]
    resources = [data.terraform_remote_state.cognito.outputs.cognito_user_pool_arn]
  }

  statement {
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
    ]
    resources = [
      data.terraform_remote_state.dynamodb.outputs.table_arn,
      "${data.terraform_remote_state.dynamodb.outputs.table_arn}/index/*",
    ]
  }

  statement {
    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue",
    ]
    resources = [data.terraform_remote_state.cognito.outputs.notify_api_key_secret_arn]
  }
}

resource "aws_iam_policy" "app_backend_access" {
  name   = "hackathon-2026-hosting-app-backend"
  policy = data.aws_iam_policy_document.app_backend_access.json
}

resource "aws_iam_role_policy_attachment" "app_backend_access" {
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app_backend_access.arn
}

resource "aws_iam_instance_profile" "app" {
  name = "hackathon-2026-hosting-ec2"
  role = aws_iam_role.app.name

  tags = local.common_tags
}
