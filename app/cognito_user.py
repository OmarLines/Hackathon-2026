from __future__ import annotations

import time
from random import SystemRandom
from typing import Any


_secure_random = SystemRandom()


class TemporaryPasswordGenerator:
    WORDS = [
        "anchor",
        "beacon",
        "canvas",
        "cedar",
        "copper",
        "flint",
        "harbor",
        "linen",
        "marble",
        "meadow",
        "pebble",
        "river",
        "slate",
        "willow",
    ]

    @classmethod
    def generate(cls) -> str:
        words = [_secure_random.choice(cls.WORDS).capitalize() for _ in range(3)]
        return f"{words[0]}.{words[1]}.{words[2]}1!"


class CognitoUser:
    def __init__(self, client: Any):
        self.client = client

    def create_new_user(
        self,
        userpool_id: str,
        email: str,
        suppress_message: bool = True,
    ) -> dict[str, Any]:
        import botocore.exceptions

        temporary_password = TemporaryPasswordGenerator.generate()
        max_attempts = 5
        base_delay = 1

        for attempt in range(max_attempts):
            try:
                return self.client.admin_create_user(
                    UserPoolId=userpool_id,
                    Username=email.lower(),
                    UserAttributes=[
                        {"Name": "email", "Value": email.lower()},
                        {"Name": "email_verified", "Value": "true"},
                    ],
                    TemporaryPassword=temporary_password,
                    **({"MessageAction": "SUPPRESS"} if suppress_message else {}),
                )
            except botocore.exceptions.ClientError:
                if attempt >= max_attempts - 1:
                    raise
                time.sleep(base_delay * (2**attempt))

        raise RuntimeError("Unable to create Cognito user")

    def get_user_by_email(self, userpool_id: str, email: str) -> dict[str, Any] | None:
        user_list = self.client.list_users(
            UserPoolId=userpool_id,
            Filter=f'email = "{email.lower()}"',
            Limit=1,
        )
        users = user_list.get("Users", [])
        if not users:
            return None
        return users[0]

    @staticmethod
    def get_attribute_from_user(user: dict[str, Any], attribute_name: str) -> str | None:
        attributes = user.get("Attributes", [])
        if not isinstance(attributes, list):
            return None

        for attribute in attributes:
            if not isinstance(attribute, dict):
                continue
            if str(attribute.get("Name")) != attribute_name:
                continue
            value = attribute.get("Value")
            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    def set_user_password(self, userpool_id: str, username: str, password: str) -> None:
        self.client.admin_set_user_password(
            UserPoolId=userpool_id,
            Username=username,
            Password=password,
            Permanent=True,
        )

    def delete_user(self, userpool_id: str, username: str) -> None:
        self.client.admin_delete_user(
            UserPoolId=userpool_id,
            Username=username,
        )
