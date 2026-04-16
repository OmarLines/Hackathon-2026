import uuid
import re
from datetime import date
from flask import Blueprint, render_template, request, session, redirect, url_for
from .store import referrers, referees

bp = Blueprint("main", __name__)


def require_referrer(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("type") != "referrer":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


STEPS = [
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


def next_step(current):
    idx = STEPS.index(current)
    return STEPS[idx + 1] if idx + 1 < len(STEPS) else None


def prev_step(current):
    idx = STEPS.index(current)
    return STEPS[idx - 1] if idx > 0 else None


def validate_child(data):
    errors = {}
    if not data.get("child_name", "").strip():
        errors["child_name"] = "Enter the child's name"
    day = data.get("child_dob_day", "")
    month = data.get("child_dob_month", "")
    year = data.get("child_dob_year", "")
    if not day or not month or not year:
        errors["child_dob"] = "Enter the child's date of birth"
    else:
        try:
            dob = date(int(year), int(month), int(day))
            if dob > date.today():
                errors["child_dob"] = "Date of birth must be in the past"
        except ValueError:
            errors["child_dob"] = "Enter a real date of birth"
    if not data.get("gender", "").strip():
        errors["gender"] = "Enter the child's gender"
    return errors


def validate_address(data):
    errors = {}
    if not data.get("address_line1", "").strip():
        errors["address_line1"] = "Enter the first line of the address"
    if not data.get("town", "").strip():
        errors["town"] = "Enter the town or city"
    
    postcode = data.get("postcode", "").strip().upper()
    if not postcode:
        errors["postcode"] = "Enter the postcode"
    elif not re.match(r"^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", postcode):
        errors["postcode"] = "Enter a real postcode"
        
    tel_no = data.get("tel_no", "").strip()
    if not tel_no:
        errors["tel_no"] = "Enter a telephone number"
    elif not re.match(r"^[0-9\s\+\-\(\)]{7,20}$", tel_no):
        errors["tel_no"] = "Enter a real telephone number"
        
    return errors


def validate_parent(data):
    errors = {}
    if not data.get("parent_name", "").strip():
        errors["parent_name"] = "Enter the parent or carer's name"
    
    email = data.get("parent_email", "").strip()
    if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        errors["parent_email"] = "Enter a real email address"
        
    day = data.get("parent_dob_day", "").strip()
    month = data.get("parent_dob_month", "").strip()
    year = data.get("parent_dob_year", "").strip()
    if day or month or year:
        if not day or not month or not year:
            errors["parent_dob"] = "Enter the parent's full date of birth"
        else:
            try:
                dob = date(int(year), int(month), int(day))
                if dob > date.today():
                    errors["parent_dob"] = "Date of birth must be in the past"
            except ValueError:
                errors["parent_dob"] = "Enter a real date of birth"
                
    family_tel = data.get("family_tel", "").strip()
    if family_tel and not re.match(r"^[0-9\s\+\-\(\)]{7,20}$", family_tel):
        errors["family_tel"] = "Enter a real telephone number"
        
    if not data.get("locality", "").strip():
        errors["locality"] = "Enter the locality"
    return errors


def validate_referrer(data):
    errors = {}
    if not data.get("referrer_name", "").strip():
        errors["referrer_name"] = "Enter the referrer's name"
    if not data.get("role_agency", "").strip():
        errors["role_agency"] = "Enter the role or agency"
    day = data.get("referral_date_day", "").strip()
    month = data.get("referral_date_month", "").strip()
    year = data.get("referral_date_year", "").strip()
    if not day or not month or not year:
        errors["referral_date"] = "Enter the date of referral"
    else:
        try:
            ref_date = date(int(year), int(month), int(day))
            if ref_date > date.today():
                errors["referral_date"] = "Date of referral must be in the past"
        except ValueError:
            errors["referral_date"] = "Enter a real date of referral"
    return errors


def validate_service_type(data):
    errors = {}
    if not data.get("service_type"):
        errors["service_type"] = "Select a service type"
    return errors


def validate_service_selection(data):
    errors = {}
    if not data.get("service"):
        errors["service"] = "Select a service"
    return errors


def validate_consent(data):
    errors = {}
    if not data.get("registered_sure_start"):
        errors["registered_sure_start"] = (
            "Confirm the family is registered with Sure Start Children's Centre"
        )
    if not data.get("verbal_consent"):
        errors["verbal_consent"] = "Select whether verbal consent was given"
    return errors


VALIDATORS = {
    "child": validate_child,
    "address": validate_address,
    "parent": validate_parent,
    "referrer": validate_referrer,
    "service_type": validate_service_type,
    "service_selection": validate_service_selection,
    "consent": validate_consent,
}

FORM_FIELDS = {
    "child": [
        "child_name",
        "child_dob_day",
        "child_dob_month",
        "child_dob_year",
        "gender",
    ],
    "address": ["address_line1", "address_line2", "town", "postcode", "tel_no"],
    "parent": [
        "parent_name",
        "parent_email",
        "parent_dob_day",
        "parent_dob_month",
        "parent_dob_year",
        "family_tel",
        "locality",
    ],
    "referrer": [
        "referrer_name",
        "role_agency",
        "referral_date_day",
        "referral_date_month",
        "referral_date_year",
    ],
    "service_type": ["service_type"],
    "service_selection": ["service"],
    "additional_info": ["additional_info"],
    "consent": ["registered_sure_start", "verbal_consent"],
}

SERVICE_OPTIONS = {
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

SERVICE_LABELS = {
    v: label for options in SERVICE_OPTIONS.values() for v, label in options
}


@bp.route("/")
def index():
    user = session.get("user")
    if user:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/apply/start")
@require_referrer
def start():
    session.pop("answers", None)
    return redirect(url_for("main.step", step_name="child"))


@bp.route("/apply/<step_name>", methods=["GET", "POST"])
@require_referrer
def step(step_name):
    if step_name not in STEPS or step_name in ("check", "confirmation"):
        return redirect(url_for("main.index"))

    answers = session.get("answers", {})
    errors = {}

    if step_name == "service_selection" and not answers.get("service_type"):
        return redirect(url_for("main.step", step_name="service_type"))

    if request.method == "POST":
        form_data = request.form.to_dict()
        if step_name == "consent":
            form_data["registered_sure_start"] = form_data.get(
                "registered_sure_start", ""
            )

        validator = VALIDATORS.get(step_name)
        if validator:
            errors = validator(form_data)

        if not errors:
            for field in FORM_FIELDS.get(step_name, []):
                answers[field] = form_data.get(field, "")
            session["answers"] = answers
            return redirect(url_for("main.step", step_name=next_step(step_name)))

    extra = {}
    if step_name == "service_selection":
        service_type = answers.get("service_type", "prevention")
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
def check():
    answers = session.get("answers", {})
    if not answers:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        ref = str(uuid.uuid4())[:8].upper()
        session["ref"] = ref

        # Create referee account from submitted answers
        referees[ref] = {
            "ref_number": ref,
            "child_name": answers.get("child_name", ""),
            "postcode": answers.get("postcode", ""),
            "answers": dict(answers),
            "referrer_email": session["user"]["email"],
        }

        # Associate referral with the referrer
        referrer = referrers.get(session["user"]["email"])
        if referrer is not None:
            referrer["referrals"].append(ref)

        return redirect(url_for("main.confirmation"))

    return render_template(
        "steps/check.html",
        answers=answers,
        service_labels=SERVICE_LABELS,
        prev_step="consent",
    )


@bp.route("/apply/confirmation")
@require_referrer
def confirmation():
    ref = session.get("ref")
    if not ref:
        return redirect(url_for("main.index"))
    referee = referees.get(ref, {})
    return render_template(
        "steps/confirmation.html", ref=ref, postcode=referee.get("postcode", "")
    )
