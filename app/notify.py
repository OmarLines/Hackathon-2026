import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from notifications_python_client import NotificationsAPIClient

logger = logging.getLogger(__name__)

# Placeholder names for the secrets stored in AWS Secrets Manager.
# Replace these with the real secret names when deploying.
_API_KEY_SECRET_NAME = "GOVNOTIFY_API_KEY"
_TEMPLATE_ID_SECRET_NAME = "GOVNOTIFY_REFEREE_TEMPLATE_ID"


def _get_secret(secret_name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    # Secrets Manager returns either SecretString or SecretBinary
    secret = response.get("SecretString") or response["SecretBinary"].decode()
    # Support both plain strings and JSON-wrapped values {"value": "..."}
    try:
        parsed = json.loads(secret)
        return parsed.get("value", secret)
    except (json.JSONDecodeError, AttributeError):
        return secret


def send_referee_credentials(to_email: str, ref_number: str, postcode: str) -> None:
    """Send the referee their login credentials via GOV.UK Notify.

    Raises nothing — errors are logged so a failed send never blocks
    the form submission.
    """
    if not to_email:
        logger.info("No referee email address; skipping Notify send for ref %s", ref_number)
        return

    try:
        api_key = _get_secret(_API_KEY_SECRET_NAME)
        template_id = _get_secret(_TEMPLATE_ID_SECRET_NAME)

        client = NotificationsAPIClient(api_key)
        client.send_email_notification(
            email_address=to_email,
            template_id=template_id,
            personalisation={
                "reference_number": ref_number,
                "postcode": postcode,
            },
        )
        logger.info("Notify email sent to %s for ref %s", to_email, ref_number)

    except (BotoCoreError, ClientError) as exc:
        logger.error("Failed to retrieve Notify secrets from AWS: %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send Notify email for ref %s: %s", ref_number, exc)
