from __future__ import annotations

import json

from flask import current_app


def get_admin_credentials() -> dict[str, str] | None:
    backend_name = str(current_app.config.get("APP_BACKEND", "local")).lower()
    if backend_name == "aws":
        return _get_aws_admin_credentials()

    username = current_app.config.get("ADMIN_USERNAME")
    password = current_app.config.get("ADMIN_PASSWORD")
    if (
        isinstance(username, str)
        and isinstance(password, str)
        and username
        and password
    ):
        return {"username": username, "password": password}
    return None


def _get_aws_admin_credentials() -> dict[str, str] | None:
    secret_name = current_app.config.get("ADMIN_CREDENTIALS_SECRET_NAME")
    if not isinstance(secret_name, str) or not secret_name.strip():
        return None

    cache = current_app.extensions.setdefault("admin_credentials_cache", {})
    cached = cache.get(secret_name)
    if isinstance(cached, dict):
        return cached

    import boto3

    secretsmanager = current_app.extensions.get("admin_credentials_secretsmanager")
    if secretsmanager is None:
        secretsmanager = boto3.client(
            "secretsmanager",
            region_name=current_app.config.get("AWS_REGION", "eu-west-2"),
        )
        current_app.extensions["admin_credentials_secretsmanager"] = secretsmanager

    response = secretsmanager.get_secret_value(SecretId=secret_name)
    secret_string = response.get("SecretString")
    if not isinstance(secret_string, str) or not secret_string.strip():
        raise RuntimeError("Admin credentials secret has no SecretString")

    payload = json.loads(secret_string)
    if not isinstance(payload, dict):
        raise RuntimeError("Admin credentials secret must be a JSON object")

    username = payload.get("username")
    password = payload.get("password")
    if not isinstance(username, str) or not username.strip():
        raise RuntimeError("Admin credentials secret is missing username")
    if not isinstance(password, str) or not password.strip():
        raise RuntimeError("Admin credentials secret is missing password")

    credentials = {"username": username, "password": password}
    cache[secret_name] = credentials
    return credentials
