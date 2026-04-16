from __future__ import annotations

import os


def get_cognito_idp_client(aws_region: str):
    import boto3

    aws_endpoint = os.getenv("AWS_ENDPOINT")
    if aws_endpoint:
        return boto3.client("cognito-idp", endpoint_url=aws_endpoint, region_name=aws_region)
    return boto3.client("cognito-idp", region_name=aws_region)
