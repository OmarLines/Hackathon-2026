import os

from flask import Flask

from .backend import build_backend
from .notifications import build_notifier
from .routes import bp
from .auth import auth_bp


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-change-in-production"
    app.config.update(
        APP_BACKEND=os.getenv("APP_BACKEND", "local"),
        AWS_REGION=os.getenv("AWS_REGION", "eu-west-2"),
        COGNITO_USER_POOL_CLIENT_ID=os.getenv("COGNITO_USER_POOL_CLIENT_ID"),
        COGNITO_USER_POOL_ID=os.getenv("COGNITO_USER_POOL_ID"),
        CURRENT_FORM_ID=os.getenv("CURRENT_FORM_ID", "children-centre-services"),
        NOTIFY_API_KEY_SECRET_NAME=os.getenv("NOTIFY_API_KEY_SECRET_NAME"),
        NOTIFY_REFERRAL_LOGIN_DETAILS_TEMPLATE_ID=os.getenv(
            "NOTIFY_REFERRAL_LOGIN_DETAILS_TEMPLATE_ID"
        ),
        NOTIFY_REFERRER_REGISTRATION_TEMPLATE_ID=os.getenv(
            "NOTIFY_REFERRER_REGISTRATION_TEMPLATE_ID"
        ),
        REFERRALS_TABLE_NAME=os.getenv("REFERRALS_TABLE_NAME"),
        REFERRER_PASSWORD_MIN_LENGTH=int(
            os.getenv("REFERRER_PASSWORD_MIN_LENGTH", "8")
        ),
        REFERRER_PASSWORD_REQUIRE_LOWERCASE=_env_bool(
            "REFERRER_PASSWORD_REQUIRE_LOWERCASE", False
        ),
        REFERRER_PASSWORD_REQUIRE_NUMBERS=_env_bool(
            "REFERRER_PASSWORD_REQUIRE_NUMBERS", False
        ),
        REFERRER_PASSWORD_REQUIRE_SYMBOLS=_env_bool(
            "REFERRER_PASSWORD_REQUIRE_SYMBOLS", False
        ),
        REFERRER_PASSWORD_REQUIRE_UPPERCASE=_env_bool(
            "REFERRER_PASSWORD_REQUIRE_UPPERCASE", False
        ),
        SERVICE_NAME=os.getenv("SERVICE_NAME", "Request for Children's Centre Service"),
    )
    app.extensions["app_backend"] = build_backend(app.config)
    app.extensions["registration_notifier"] = build_notifier(app.config)
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp)
    return app
