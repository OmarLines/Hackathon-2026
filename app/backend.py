from __future__ import annotations

from contextlib import suppress
import uuid
from datetime import UTC, datetime
from typing import Any, Protocol

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from .aws_cognito import get_cognito_idp_client
from .cognito_user import CognitoUser
from .store import referees, referrers


class DuplicateReferrerError(RuntimeError):
    pass


class BackendConfigurationError(RuntimeError):
    pass


class InvalidReferrerPasswordError(RuntimeError):
    pass


class InvalidReferrerEmailError(RuntimeError):
    pass


class AppBackend(Protocol):
    def authenticate_referee(
        self, ref_number: str, postcode: str
    ) -> dict[str, Any] | None: ...
    def authenticate_referrer(
        self, email: str, password: str
    ) -> dict[str, Any] | None: ...
    def create_referral(
        self, user: dict[str, Any], answers: dict[str, Any], ref_number: str
    ) -> dict[str, Any]: ...
    def get_referral(self, ref_number: str) -> dict[str, Any] | None: ...
    def update_referral_status(self, ref_number: str, status: str) -> None: ...
    def get_referrer_profile(self, user: dict[str, Any]) -> dict[str, Any]: ...
    def hydrate_referrer_user(self, user: dict[str, Any]) -> dict[str, Any] | None: ...
    def has_form_access(self, user: dict[str, Any], form_id: str) -> bool: ...
    def list_referrals_for_referrer(
        self, user: dict[str, Any]
    ) -> list[dict[str, Any]]: ...
    def register_referrer(
        self, name: str, email: str, password: str
    ) -> dict[str, Any]: ...


def build_backend(config: dict[str, Any]) -> AppBackend:
    backend_name = config.get("APP_BACKEND", "local").lower()
    form_id = config.get("CURRENT_FORM_ID", "children-centre-services")

    if backend_name == "local":
        return LocalBackend(form_id=form_id)
    if backend_name == "aws":
        return AwsBackend(
            aws_region=config.get("AWS_REGION", "eu-west-2"),
            form_id=form_id,
            referrals_table_name=config.get("REFERRALS_TABLE_NAME"),
            user_pool_client_id=config.get("COGNITO_USER_POOL_CLIENT_ID"),
            user_pool_id=config.get("COGNITO_USER_POOL_ID"),
        )

    raise BackendConfigurationError(f"Unsupported app backend: {backend_name}")


def get_backend() -> AppBackend:
    return current_app.extensions["app_backend"]


def _normalise_postcode(postcode: str) -> str:
    return postcode.strip().upper().replace(" ", "")


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class LocalBackend:
    def __init__(self, form_id: str) -> None:
        self.form_id = form_id

    def register_referrer(self, name: str, email: str, password: str) -> dict[str, Any]:
        if email in referrers:
            raise DuplicateReferrerError

        user_id = str(uuid.uuid4())
        referrers[email] = {
            "form_access": {self.form_id},
            "name": name,
            "password_hash": generate_password_hash(password),
            "referrals": [],
            "sub": user_id,
        }
        return self._session_user(email, referrers[email])

    def authenticate_referrer(self, email: str, password: str) -> dict[str, Any] | None:
        referrer = referrers.get(email)
        if not referrer or not check_password_hash(referrer["password_hash"], password):
            return None
        self._ensure_referrer_defaults(email, referrer)
        return self._session_user(email, referrer)

    def authenticate_referee(
        self, ref_number: str, postcode: str
    ) -> dict[str, Any] | None:
        referral = referees.get(ref_number)
        if not referral:
            return None
        if referral["postcode_normalized"] != _normalise_postcode(postcode):
            return None
        return {
            "name": referral["child_name"],
            "ref_number": ref_number,
            "type": "referee",
        }

    def get_referrer_profile(self, user: dict[str, Any]) -> dict[str, Any]:
        referrer = referrers.get(user["email"], {})
        return {
            "email": user["email"],
            "name": referrer.get("name", user.get("name", user["email"])),
            "sub": referrer.get("sub", user.get("sub")),
        }

    def hydrate_referrer_user(self, user: dict[str, Any]) -> dict[str, Any] | None:
        email = user.get("email")
        if not isinstance(email, str) or not email:
            return None
        referrer = referrers.get(email)
        if not referrer:
            return None
        self._ensure_referrer_defaults(email, referrer)
        return self._session_user(email, referrer)

    def has_form_access(self, user: dict[str, Any], form_id: str) -> bool:
        referrer = referrers.get(user["email"])
        if not referrer:
            return False
        self._ensure_referrer_defaults(user["email"], referrer)
        return form_id in referrer["form_access"]

    def list_referrals_for_referrer(self, user: dict[str, Any]) -> list[dict[str, Any]]:
        referrer = referrers.get(user["email"], {})
        referral_ids = referrer.get("referrals", [])
        return [referees[ref] for ref in referral_ids if ref in referees]

    def create_referral(
        self, user: dict[str, Any], answers: dict[str, Any], ref_number: str
    ) -> dict[str, Any]:
        created_at = _utc_now_iso()
        referral = {
            "answers": dict(answers),
            "child_name": answers.get("child_name", ""),
            "created_at": created_at,
            "form_id": self.form_id,
            "postcode": answers.get("postcode", ""),
            "postcode_normalized": _normalise_postcode(answers.get("postcode", "")),
            "ref_number": ref_number,
            "referrer_email": user["email"],
            "referrer_name": user.get("name", ""),
            "status": "sent",
            "user_id": user.get("sub"),
        }
        referees[ref_number] = referral

        referrer = referrers.get(user["email"])
        if referrer is not None:
            self._ensure_referrer_defaults(user["email"], referrer)
            referrer["referrals"].append(ref_number)

        return referral

    def get_referral(self, ref_number: str) -> dict[str, Any] | None:
        return referees.get(ref_number)

    def update_referral_status(self, ref_number: str, status: str) -> None:
        referral = referees.get(ref_number)
        if referral:
            referral["status"] = status

    def _ensure_referrer_defaults(self, email: str, referrer: dict[str, Any]) -> None:
        referrer.setdefault("form_access", {self.form_id})
        referrer.setdefault("referrals", [])
        referrer.setdefault(
            "sub", str(uuid.uuid5(uuid.NAMESPACE_URL, f"local-referrer:{email}"))
        )

    def _session_user(self, email: str, referrer: dict[str, Any]) -> dict[str, Any]:
        return {
            "email": email,
            "name": referrer["name"],
            "sub": referrer["sub"],
            "type": "referrer",
        }


class AwsBackend:
    def __init__(
        self,
        aws_region: str,
        form_id: str,
        referrals_table_name: str | None,
        user_pool_client_id: str | None,
        user_pool_id: str | None,
    ) -> None:
        missing = {
            "COGNITO_USER_POOL_CLIENT_ID": user_pool_client_id,
            "COGNITO_USER_POOL_ID": user_pool_id,
            "REFERRALS_TABLE_NAME": referrals_table_name,
        }
        missing_keys = [name for name, value in missing.items() if not value]
        if missing_keys:
            raise BackendConfigurationError(
                f"AWS backend requires configuration for: {', '.join(sorted(missing_keys))}"
            )

        self.aws_region = aws_region
        self.form_id = form_id
        self.user_pool_id = user_pool_id or ""
        self.user_pool_client_id = user_pool_client_id or ""
        import boto3

        self.cognito = get_cognito_idp_client(aws_region)
        self.cognito_user = CognitoUser(client=self.cognito)
        self.dynamodb = boto3.resource("dynamodb", region_name=aws_region)
        self.table = self.dynamodb.Table(referrals_table_name or "")

    def register_referrer(self, name: str, email: str, password: str) -> dict[str, Any]:
        from botocore.exceptions import ClientError

        created_cognito_user = False
        try:
            self.cognito_user.create_new_user(
                email=email,
                suppress_message=True,
                userpool_id=self.user_pool_id,
            )
            created_cognito_user = True
            self.cognito_user.set_user_password(
                password=password,
                userpool_id=self.user_pool_id,
                username=email,
            )
        except ClientError as error:
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"].get("Message", "")
            if error_code in {"AliasExistsException", "UsernameExistsException"}:
                raise DuplicateReferrerError from error
            if created_cognito_user:
                with suppress(Exception):
                    self.cognito_user.delete_user(
                        userpool_id=self.user_pool_id, username=email
                    )
            if error_code == "InvalidPasswordException":
                raise InvalidReferrerPasswordError(
                    error_message or "Password does not meet the required policy"
                ) from error
            if error_code == "InvalidParameterException":
                lowered_message = error_message.lower()
                if "username should be an email" in lowered_message:
                    raise InvalidReferrerEmailError(error_message) from error
                if "password" in lowered_message:
                    raise InvalidReferrerPasswordError(
                        error_message or "Password does not meet the required policy"
                    ) from error
            raise

        cognito_user = self.cognito_user.get_user_by_email(
            userpool_id=self.user_pool_id, email=email
        )
        if not cognito_user:
            raise RuntimeError(
                f"Unable to load Cognito user after registration for {email}"
            )
        user_sub = self.cognito_user.get_attribute_from_user(cognito_user, "sub")
        if not user_sub:
            raise RuntimeError(f"Cognito user for {email} is missing sub")

        created_at = _utc_now_iso()
        self.table.put_item(
            Item={
                "created_at": created_at,
                "email": email,
                "entity_type": "REFERRER_PROFILE",
                "name": name,
                "pk": self._user_pk(user_sub),
                "sk": "PROFILE",
                "user_id": user_sub,
            },
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )
        self.table.put_item(
            Item={
                "access_level": "referrer",
                "created_at": created_at,
                "entity_type": "FORM_ACCESS",
                "form_id": self.form_id,
                "pk": self._user_pk(user_sub),
                "sk": self._form_access_sk(self.form_id),
                "user_id": user_sub,
            },
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )

        return {
            "email": email,
            "name": name,
            "sub": user_sub,
            "type": "referrer",
        }

    def authenticate_referrer(self, email: str, password: str) -> dict[str, Any] | None:
        from botocore.exceptions import ClientError

        try:
            self.cognito.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"PASSWORD": password, "USERNAME": email},
                ClientId=self.user_pool_client_id,
            )
        except ClientError as error:
            error_code = error.response["Error"]["Code"]
            if error_code in {
                "NotAuthorizedException",
                "PasswordResetRequiredException",
                "UserNotConfirmedException",
                "UserNotFoundException",
            }:
                return None
            raise

        cognito_user = self.cognito_user.get_user_by_email(
            userpool_id=self.user_pool_id, email=email
        )
        if not cognito_user:
            return None
        user_sub = self.cognito_user.get_attribute_from_user(cognito_user, "sub")
        if not user_sub:
            raise RuntimeError(f"Cognito user for {email} is missing sub")
        profile = self.get_referrer_profile({"email": email, "sub": user_sub})

        return {
            "email": profile["email"],
            "name": profile["name"],
            "sub": user_sub,
            "type": "referrer",
        }

    def authenticate_referee(
        self, ref_number: str, postcode: str
    ) -> dict[str, Any] | None:
        referral = self.get_referral(ref_number)
        if not referral:
            return None
        if referral["postcode_normalized"] != _normalise_postcode(postcode):
            return None
        return {
            "name": referral["child_name"],
            "ref_number": ref_number,
            "type": "referee",
        }

    def get_referrer_profile(self, user: dict[str, Any]) -> dict[str, Any]:
        item = self.table.get_item(
            Key={"pk": self._user_pk(user["sub"]), "sk": "PROFILE"}
        ).get("Item", {})
        return {
            "email": item.get("email", user.get("email", "")),
            "name": item.get("name", user.get("name", user.get("email", ""))),
            "sub": user["sub"],
        }

    def hydrate_referrer_user(self, user: dict[str, Any]) -> dict[str, Any] | None:
        user_sub = user.get("sub")
        if isinstance(user_sub, str) and user_sub:
            profile = self.get_referrer_profile(user)
            return {
                "email": profile["email"],
                "name": profile["name"],
                "sub": user_sub,
                "type": "referrer",
            }

        email = user.get("email")
        if not isinstance(email, str) or not email:
            return None

        cognito_user = self.cognito_user.get_user_by_email(
            userpool_id=self.user_pool_id, email=email
        )
        if not cognito_user:
            return None
        resolved_sub = self.cognito_user.get_attribute_from_user(cognito_user, "sub")
        if not resolved_sub:
            return None

        profile = self.get_referrer_profile({"email": email, "sub": resolved_sub})
        return {
            "email": profile["email"],
            "name": profile["name"],
            "sub": resolved_sub,
            "type": "referrer",
        }

    def has_form_access(self, user: dict[str, Any], form_id: str) -> bool:
        item = self.table.get_item(
            Key={"pk": self._user_pk(user["sub"]), "sk": self._form_access_sk(form_id)}
        ).get("Item")
        return item is not None

    def list_referrals_for_referrer(self, user: dict[str, Any]) -> list[dict[str, Any]]:
        from boto3.dynamodb.conditions import Key

        response = self.table.query(
            KeyConditionExpression=Key("pk").eq(self._user_pk(user["sub"]))
            & Key("sk").begins_with("REFERRAL#")
        )
        items = response.get("Items", [])
        return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)

    def create_referral(
        self, user: dict[str, Any], answers: dict[str, Any], ref_number: str
    ) -> dict[str, Any]:
        referral = {
            "answers": dict(answers),
            "child_name": answers.get("child_name", ""),
            "created_at": _utc_now_iso(),
            "entity_type": "REFERRAL",
            "form_id": self.form_id,
            "gsi1pk": self._referral_lookup_pk(ref_number),
            "gsi1sk": "REFERRAL",
            "pk": self._user_pk(user["sub"]),
            "postcode": answers.get("postcode", ""),
            "postcode_normalized": _normalise_postcode(answers.get("postcode", "")),
            "ref_number": ref_number,
            "referrer_email": user["email"],
            "referrer_name": user.get("name", ""),
            "sk": self._referral_sk(ref_number),
            "status": "sent",
            "user_id": user["sub"],
        }
        self.table.put_item(
            Item=referral,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )
        return referral

    def get_referral(self, ref_number: str) -> dict[str, Any] | None:
        from boto3.dynamodb.conditions import Key

        response = self.table.query(
            IndexName="gsi1",
            KeyConditionExpression=Key("gsi1pk").eq(
                self._referral_lookup_pk(ref_number)
            )
            & Key("gsi1sk").eq("REFERRAL"),
            Limit=1,
        )
        items = response.get("Items", [])
        return items[0] if items else None

    def update_referral_status(self, ref_number: str, status: str) -> None:
        referral = self.get_referral(ref_number)
        if not referral:
            return

        self.table.update_item(
            Key={"pk": referral["pk"], "sk": referral["sk"]},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": status},
        )

    def _form_access_sk(self, form_id: str) -> str:
        return f"FORM_ACCESS#{form_id}"

    def _referral_lookup_pk(self, ref_number: str) -> str:
        return f"REFERRAL#{ref_number}"

    def _referral_sk(self, ref_number: str) -> str:
        return f"REFERRAL#{ref_number}"

    def _user_pk(self, user_sub: str) -> str:
        return f"USER#{user_sub}"
