import re
import uuid
from datetime import date
from typing import Any, Callable, TypeVar

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.typing import ResponseReturnValue

from .backend import get_backend
from .notifications import get_notifier

bp: Blueprint = Blueprint("main", __name__)

T = TypeVar("T", bound=Callable[..., Any])


def require_referrer(f: T) -> T:
    from functools import wraps

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        user: dict[str, Any] | None = session.get("user")
        if not user or user.get("type") != "referrer":
            return redirect(url_for("auth.login"))
        hydrated_user = get_backend().hydrate_referrer_user(user)
        if not hydrated_user:
            session.clear()
            return redirect(url_for("auth.login"))
        session["user"] = hydrated_user
        if not get_backend().has_form_access(
            hydrated_user, current_app.config["CURRENT_FORM_ID"]
        ):
            abort(403)
        return f(*args, **kwargs)

    return decorated  # type: ignore


STEPS: list[str] = [
    "child",
    "address",
    "parent",
    "referrer",
    "service_type",
    "service_selection",
    "additional_info",
    "consent",
    "check",
    "confirmation",
]


def next_step(current: str) -> str | None:
    idx: int = STEPS.index(current)
    return STEPS[idx + 1] if idx + 1 < len(STEPS) else None


def prev_step(current: str) -> str | None:
    idx: int = STEPS.index(current)
    return STEPS[idx - 1] if idx > 0 else None


def validate_child(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("child_name", "").strip():
        errors["child_name"] = "Enter the child's name"
    dob_str: str = data.get("child_dob", "")
    if not dob_str:
        errors["child_dob"] = "Enter the child's date of birth"
    else:
        try:
            dob: date = date.fromisoformat(dob_str)
            if dob > date.today():
                errors["child_dob"] = "Date of birth must be in the past"
        except ValueError:
            errors["child_dob"] = "Enter a real date of birth"
    if not data.get("gender", "").strip():
        errors["gender"] = "Enter the child's gender"
    return errors


def validate_address(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("address_line1", "").strip():
        errors["address_line1"] = "Enter the first line of the address"
    if not data.get("town", "").strip():
        errors["town"] = "Enter the town or city"

    postcode: str = data.get("postcode", "").strip().upper()
    if not postcode:
        errors["postcode"] = "Enter the postcode"
    elif not re.match(r"^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", postcode):
        errors["postcode"] = "Enter a real postcode"

    tel_no: str = data.get("tel_no", "").strip()
    if not tel_no:
        errors["tel_no"] = "Enter a telephone number"
    elif not re.match(r"^[0-9\s\+\-\(\)]{7,20}$", tel_no):
        errors["tel_no"] = "Enter a real telephone number"

    return errors


def validate_parent(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("parent_name", "").strip():
        errors["parent_name"] = "Enter the parent or carer's name"

    email: str = data.get("parent_email", "").strip()
    if not email:
        errors["parent_email"] = "Enter the parent or carer's email address"
    elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        errors["parent_email"] = "Enter a real email address"

    dob_str: str = data.get("parent_dob", "").strip()
    if not dob_str:
        errors["parent_dob"] = "Enter the parent or carer's date of birth"
    else:
        try:
            dob: date = date.fromisoformat(dob_str)
            if dob > date.today():
                errors["parent_dob"] = "Date of birth must be in the past"
        except ValueError:
            errors["parent_dob"] = "Enter a real date of birth"

    family_tel: str = data.get("family_tel", "").strip()
    if family_tel and not re.match(r"^[0-9\s\+\-\(\)]{7,20}$", family_tel):
        errors["family_tel"] = "Enter a real telephone number"

    if not data.get("locality", "").strip():
        errors["locality"] = "Enter the locality"
    return errors


def validate_referrer(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("referrer_name", "").strip():
        errors["referrer_name"] = "Enter the referrer's name"
    if not data.get("role_agency", "").strip():
        errors["role_agency"] = "Enter the role or agency"
    referral_date_str: str = data.get("referral_date", "").strip()
    if not referral_date_str:
        errors["referral_date"] = "Enter the date of referral"
    else:
        try:
            ref_date: date = date.fromisoformat(referral_date_str)
            if ref_date > date.today():
                errors["referral_date"] = "Date of referral must be in the past"
        except ValueError:
            errors["referral_date"] = "Enter a real date of referral"
    return errors


def validate_service_type(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("service_type"):
        errors["service_type"] = "Select a service type"
    return errors


def validate_service_selection(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("service"):
        errors["service"] = "Select a service"
    return errors


def validate_consent(data: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not data.get("registered_sure_start"):
        errors["registered_sure_start"] = (
            "Confirm the family is registered with Sure Start Children's Centre"
        )
    if not data.get("verbal_consent"):
        errors["verbal_consent"] = "Select whether verbal consent was given"
    return errors


VALIDATORS: dict[str, Callable[[dict[str, str]], dict[str, str]]] = {
    "child": validate_child,
    "address": validate_address,
    "parent": validate_parent,
    "referrer": validate_referrer,
    "service_type": validate_service_type,
    "service_selection": validate_service_selection,
    "consent": validate_consent,
}

FORM_FIELDS: dict[str, list[str]] = {
    "child": ["child_name", "child_dob", "gender"],
    "address": ["address_line1", "address_line2", "town", "postcode", "tel_no"],
    "parent": [
        "parent_name",
        "parent_email",
        "parent_dob",
        "family_tel",
        "locality",
    ],
    "referrer": ["referrer_name", "role_agency", "referral_date"],
    "service_type": ["service_type"],
    "service_selection": ["service"],
    "additional_info": ["additional_info"],
    "consent": ["registered_sure_start", "verbal_consent"],
}

SERVICE_OPTIONS: dict[str, list[tuple[str, str]]] = {
    "prevention": [
        ("brilliant_babies", "Brilliant Babies (Conception – 1 Year)"),
        ("parent_plus", "Parent Plus (9 Months – 2+ Years)"),
        ("tiny_talkers", "Tiny Talkers (1 – 2+ Years)"),
        ("great_expectations", "Great Expectations (1 – 2+ Years)"),
    ],
    "intervention": [
        ("incredible_babies", "Incredible Babies (Birth to 12 Months)"),
        ("incredible_toddlers", "Incredible Toddlers/Pre-School (1 – 6 Years)"),
        ("families_in_making", "Families in the Making (Pre-Birth)"),
        ("henry", "HENRY (0 – 4 Years)"),
        ("healthy_families", "Healthy Families Growing Up (5 – 11 Years)"),
        ("freedom_programme", "Freedom Programme (Female 16+)"),
        ("recovery_toolkit_female", "Recovery Toolkit (Female 16+)"),
        ("recovery_toolkit_children", "Recovery Toolkit (Children/YP 8+)"),
    ],
}

SERVICE_LABELS: dict[str, str] = {
    v: label for options in SERVICE_OPTIONS.values() for v, label in options
}


@bp.route("/")
def index() -> ResponseReturnValue:
    user: dict[str, Any] | None = session.get("user")
    if user:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/apply/start")
@require_referrer
def start() -> ResponseReturnValue:
    session.pop("ref", None)
    session.pop("answers", None)
    return redirect(url_for("main.step", step_name="child"))


@bp.route("/apply/<step_name>", methods=["GET", "POST"])
@require_referrer
def step(step_name: str) -> ResponseReturnValue:
    if step_name not in STEPS or step_name in ("check", "confirmation"):
        return redirect(url_for("main.index"))

    answers: dict[str, Any] = session.get("answers", {})
    errors: dict[str, str] = {}
    current_user: dict[str, Any] = session["user"]

    if step_name == "referrer":
        saved_referrer_details = get_backend().get_saved_referrer_details(current_user)
        for field in ("referrer_name", "role_agency"):
            if not answers.get(field) and saved_referrer_details.get(field):
                answers[field] = saved_referrer_details[field]

    if step_name == "service_selection" and not answers.get("service_type"):
        return redirect(url_for("main.step", step_name="service_type"))

    if request.method == "POST":
        form_data: dict[str, str] = request.form.to_dict()
        if step_name == "consent":
            form_data["registered_sure_start"] = form_data.get(
                "registered_sure_start", ""
            )

        # Temporarily update answers with submitted data so it persists on error
        for field in FORM_FIELDS.get(step_name, []):
            answers[field] = form_data.get(field, "")

        validator: Callable[[dict[str, str]], dict[str, str]] | None = VALIDATORS.get(
            step_name
        )
        if validator:
            errors = validator(form_data)

        if not errors:
            if step_name == "referrer":
                referrer_name = str(answers.get("referrer_name", "")).strip()
                role_agency = str(answers.get("role_agency", "")).strip()
                answers["referrer_name"] = referrer_name
                answers["role_agency"] = role_agency
                get_backend().save_referrer_details(
                    current_user,
                    referrer_name=referrer_name,
                    role_agency=role_agency,
                )
            session["answers"] = answers
            return redirect(url_for("main.step", step_name=next_step(step_name)))

    extra: dict[str, Any] = {}
    if step_name == "service_selection":
        service_type: str = answers.get("service_type", "prevention")
        extra["service_options"] = SERVICE_OPTIONS.get(service_type, [])
        extra["service_type_label"] = (
            "Prevention" if service_type == "prevention" else "Intervention"
        )

    extra["prev_step"] = prev_step(step_name)

    return render_template(
        f"steps/{step_name}.html", answers=answers, errors=errors, **extra
    )


@bp.route("/apply/check", methods=["GET", "POST"])
@require_referrer
def check() -> ResponseReturnValue:
    answers: dict[str, Any] = session.get("answers", {})
    if not answers:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        ref: str = str(uuid.uuid4())[:8].upper()
        session["ref"] = ref
        referral = get_backend().create_referral(
            user=session["user"],
            answers=answers,
            ref_number=ref,
        )

        parent_email = str(answers.get("parent_email", "")).strip().lower()
        if parent_email:
            try:
                get_notifier().send_referral_login_details_email(
                    email_address=parent_email,
                    ref_number=ref,
                    postcode=str(referral.get("postcode", "")),
                )
            except Exception:
                current_app.logger.exception(
                    "Failed to send referral login details email for %s",
                    ref,
                )

        return redirect(url_for("main.confirmation"))

    return render_template(
        "steps/check.html",
        answers=answers,
        service_labels=SERVICE_LABELS,
        prev_step="consent",
    )


@bp.route("/apply/confirmation")
@require_referrer
def confirmation() -> ResponseReturnValue:
    ref: str | None = session.get("ref")
    if not ref:
        return redirect(url_for("main.index"))
    referee = get_backend().get_referral(ref) or {}
    return render_template(
        "steps/confirmation.html", ref=ref, postcode=referee.get("postcode", "")
    )


@bp.route("/referral/<ref_number>/accept", methods=["POST"])
def accept_referral(ref_number: str) -> ResponseReturnValue:
    user = session.get("user")
    if (
        not user
        or user.get("type") != "referee"
        or user.get("ref_number") != ref_number
    ):
        abort(403)

    get_backend().update_referral_status(ref_number, "accepted")
    return redirect(url_for("auth.dashboard"))
