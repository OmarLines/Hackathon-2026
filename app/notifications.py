from __future__ import annotations

import json
from typing import Any, Protocol

from flask import current_app


class AppNotifier(Protocol):
    def send_referrer_registration_email(self, email_address: str, name: str, sign_in_url: str) -> None: ...
    def send_referral_login_details_email(
        self,
        email_address: str,
        ref_number: str,
        postcode: str,
    ) -> None: ...


def build_notifier(config: dict[str, Any]) -> AppNotifier:
    referral_login_details_template_id = config.get(
        "NOTIFY_REFERRAL_LOGIN_DETAILS_TEMPLATE_ID"
    )
    registration_template_id = config.get("NOTIFY_REFERRER_REGISTRATION_TEMPLATE_ID")
    secret_name = config.get("NOTIFY_API_KEY_SECRET_NAME")

    if not secret_name:
        return NullNotifier()

    return NotifyNotifier(
        aws_region=config.get("AWS_REGION", "eu-west-2"),
        notify_api_key_secret_name=secret_name,
        referral_login_details_template_id=referral_login_details_template_id,
        registration_template_id=registration_template_id,
        service_name=config.get("SERVICE_NAME", "Request for Children's Centre Service"),
    )


def get_notifier() -> AppNotifier:
    return current_app.extensions["registration_notifier"]


class NullNotifier:
    def send_referrer_registration_email(self, email_address: str, name: str, sign_in_url: str) -> None:
        return None

    def send_referral_login_details_email(
        self,
        email_address: str,
        ref_number: str,
        postcode: str,
    ) -> None:
        return None


class NotifyNotifier:
    def __init__(
        self,
        aws_region: str,
        notify_api_key_secret_name: str,
        referral_login_details_template_id: str | None,
        registration_template_id: str | None,
        service_name: str,
    ) -> None:
        import boto3
        from notifications_python_client.notifications import NotificationsAPIClient

        self.notification_client_cls = NotificationsAPIClient
        self.notify_api_key_secret_name = notify_api_key_secret_name
        self.secretsmanager = boto3.client("secretsmanager", region_name=aws_region)
        self.referral_login_details_template_id = referral_login_details_template_id
        self.registration_template_id = registration_template_id
        self.service_name = service_name
        self._api_key: str | None = None

    def send_referrer_registration_email(self, email_address: str, name: str, sign_in_url: str) -> None:
        if not self.registration_template_id:
            return None

        client = self.notification_client_cls(api_key=self._get_api_key())
        client.send_email_notification(
            email_address=email_address,
            template_id=self.registration_template_id,
            personalisation={
                "name": name,
                "service_name": self.service_name,
                "sign_in_url": sign_in_url,
            },
        )

    def send_referral_login_details_email(
        self,
        email_address: str,
        ref_number: str,
        postcode: str,
    ) -> None:
        if not self.referral_login_details_template_id:
            return None

        client = self.notification_client_cls(api_key=self._get_api_key())
        client.send_email_notification(
            email_address=email_address,
            template_id=self.referral_login_details_template_id,
            personalisation={
                "ref_number": ref_number,
                "postcode": postcode,
            },
        )

    def _get_api_key(self) -> str:
        if self._api_key:
            return self._api_key

        response = self.secretsmanager.get_secret_value(SecretId=self.notify_api_key_secret_name)
        secret_string = response.get("SecretString")
        if not secret_string:
            raise RuntimeError("Notify API key secret has no SecretString")

        try:
            secret_payload = json.loads(secret_string)
            if isinstance(secret_payload, dict):
                api_key = secret_payload.get("gov_notify_api_key")
                if isinstance(api_key, str) and api_key.strip():
                    self._api_key = api_key
                    return api_key
        except Exception:
            pass

        if secret_string.strip():
            self._api_key = secret_string
            return secret_string

        raise RuntimeError("Notify API key secret is missing gov_notify_api_key")
