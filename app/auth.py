import re

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .backend import (
    DuplicateReferrerError,
    InvalidReferrerEmailError,
    InvalidReferrerPasswordError,
    get_backend,
)
from .notifications import get_notifier

auth_bp = Blueprint("auth", __name__)


def _build_password_hint(config: dict[str, object]) -> str:
    min_length = int(config.get("REFERRER_PASSWORD_MIN_LENGTH", 8) or 8)
    required_parts = []

    if config.get("REFERRER_PASSWORD_REQUIRE_UPPERCASE"):
        required_parts.append("upper")
    if config.get("REFERRER_PASSWORD_REQUIRE_LOWERCASE"):
        required_parts.append("lower")

    trailing_parts = []
    if config.get("REFERRER_PASSWORD_REQUIRE_NUMBERS"):
        trailing_parts.append("a number")
    if config.get("REFERRER_PASSWORD_REQUIRE_SYMBOLS"):
        trailing_parts.append("a symbol")

    if required_parts:
        trailing_parts.insert(0, f"{' and '.join(required_parts)} case letters")

    if not trailing_parts:
        return f"Must be at least {min_length} characters"

    trailing = ", ".join(trailing_parts[:-1])
    if trailing:
        trailing = f"{trailing} and {trailing_parts[-1]}"
    else:
        trailing = trailing_parts[-1]
    return f"Must be at least {min_length} characters and include {trailing}"


def _password_meets_policy(password: str, config: dict[str, object]) -> bool:
    if len(password) < int(config.get("REFERRER_PASSWORD_MIN_LENGTH", 8) or 8):
        return False
    if config.get("REFERRER_PASSWORD_REQUIRE_LOWERCASE") and not any(
        char.islower() for char in password
    ):
        return False
    if config.get("REFERRER_PASSWORD_REQUIRE_UPPERCASE") and not any(
        char.isupper() for char in password
    ):
        return False
    if config.get("REFERRER_PASSWORD_REQUIRE_NUMBERS") and not any(
        char.isdigit() for char in password
    ):
        return False
    if config.get("REFERRER_PASSWORD_REQUIRE_SYMBOLS") and not any(
        not char.isalnum() for char in password
    ):
        return False
    return True


def _password_error(config: dict[str, object]) -> str:
    return "Password " + _build_password_hint(config).replace("Must", "must", 1)


def _email_is_valid(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    if session.get("user"):
        return redirect(url_for("auth.dashboard"))

    errors = {}
    password_hint = _build_password_hint(current_app.config)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name:
            errors["name"] = "Enter your full name"
        if not email:
            errors["email"] = "Enter your email address"
        elif not _email_is_valid(email):
            errors["email"] = "Enter a real email address"
        if not password:
            errors["password"] = "Enter a password"
        elif not _password_meets_policy(password, current_app.config):
            errors["password"] = _password_error(current_app.config)
        if not confirm:
            errors["confirm_password"] = "Confirm your password"
        elif password and confirm != password:
            errors["confirm_password"] = "Passwords do not match"

        if not errors:
            try:
                session["user"] = get_backend().register_referrer(
                    name=name, email=email, password=password
                )
                sign_in_url = url_for("auth.login", _external=True)
                try:
                    get_notifier().send_referrer_registration_email(
                        email_address=email,
                        name=name,
                        sign_in_url=sign_in_url,
                    )
                except Exception:
                    current_app.logger.exception(
                        "Failed to send referrer registration email for %s",
                        email,
                    )
                return redirect(url_for("auth.dashboard"))
            except DuplicateReferrerError:
                errors["email"] = "An account with this email address already exists"
            except InvalidReferrerEmailError:
                errors["email"] = "Enter a real email address"
            except InvalidReferrerPasswordError:
                errors["password"] = _password_error(current_app.config)

    return render_template(
        "register.html",
        errors=errors,
        form=request.form if request.method == "POST" else {},
        password_hint=password_hint,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if session.get("user"):
        return redirect(url_for("auth.dashboard"))

    errors = {}

    if request.method == "POST":
        user_type = request.form.get("user_type", "")

        if not user_type:
            errors["user_type"] = "Select how you are accessing the service"

        elif user_type == "referrer":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = get_backend().authenticate_referrer(email=email, password=password)
            if user:
                session["user"] = user
                return redirect(url_for("auth.dashboard"))
            errors["referrer_login"] = (
                "Either your username and password are incorrect, "
                "or you are not registered with this service."
            )

        elif user_type == "referee":
            ref_number = request.form.get("ref_number", "").strip().upper()
            postcode = request.form.get("postcode", "").strip().upper().replace(" ", "")
            user = get_backend().authenticate_referee(
                ref_number=ref_number, postcode=postcode
            )
            if user:
                session["user"] = user
                return redirect(url_for("auth.dashboard"))
            errors["referee_login"] = "Incorrect reference number or postcode"

    return render_template(
        "login.html",
        errors=errors,
        form=request.form if request.method == "POST" else {},
    )


@auth_bp.route("/logout")
def logout() -> Response | str:
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard() -> Response | str:
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    if user["type"] == "referrer":
        hydrated_user = get_backend().hydrate_referrer_user(user)
        if not hydrated_user:
            session.clear()
            return redirect(url_for("auth.login"))
        session["user"] = hydrated_user
        profile = get_backend().get_referrer_profile(hydrated_user)
        user = {**hydrated_user, "name": profile["name"]}
        submitted = get_backend().list_referrals_for_referrer(hydrated_user)
        return render_template(
            "dashboard_referrer.html", user=user, referrals=submitted
        )

    referee = get_backend().get_referral(user["ref_number"]) or {}
    return render_template("dashboard_referee.html", user=user, referral=referee)
