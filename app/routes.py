import uuid
from datetime import date
from flask import Blueprint, render_template, request, session, redirect, url_for

bp = Blueprint("main", __name__)

STEPS = ["name", "dob", "address", "licence_type", "previous_licence", "declaration", "check", "confirmation"]


def next_step(current):
    idx = STEPS.index(current)
    return STEPS[idx + 1] if idx + 1 < len(STEPS) else None


def validate_name(data):
    errors = {}
    if not data.get("full_name", "").strip():
        errors["full_name"] = "Enter your full name"
    return errors


def validate_dob(data):
    errors = {}
    day, month, year = data.get("dob_day", ""), data.get("dob_month", ""), data.get("dob_year", "")
    if not day or not month or not year:
        errors["dob"] = "Enter your date of birth"
        return errors
    try:
        dob = date(int(year), int(month), int(day))
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            errors["dob"] = "You must be 18 or over to apply"
        if dob > today:
            errors["dob"] = "Date of birth must be in the past"
    except ValueError:
        errors["dob"] = "Enter a real date of birth"
    return errors


def validate_address(data):
    errors = {}
    if not data.get("address_line1", "").strip():
        errors["address_line1"] = "Enter the first line of your address"
    if not data.get("town", "").strip():
        errors["town"] = "Enter your town or city"
    postcode = data.get("postcode", "").strip()
    if not postcode:
        errors["postcode"] = "Enter your postcode"
    return errors


def validate_licence_type(data):
    errors = {}
    if not data.get("licence_type"):
        errors["licence_type"] = "Select a licence type"
    return errors


def validate_declaration(data):
    errors = {}
    if not data.get("declaration"):
        errors["declaration"] = "You must agree to the declaration to submit"
    return errors


VALIDATORS = {
    "name": validate_name,
    "dob": validate_dob,
    "address": validate_address,
    "licence_type": validate_licence_type,
    "declaration": validate_declaration,
}

FORM_FIELDS = {
    "name": ["full_name"],
    "dob": ["dob_day", "dob_month", "dob_year"],
    "address": ["address_line1", "address_line2", "address_line3", "town", "postcode"],
    "licence_type": ["licence_type"],
    "previous_licence": ["previous_licence_number"],
    "declaration": ["declaration"],
}


@bp.route("/")
def index():
    session.clear()
    return redirect(url_for("main.step", step_name="name"))


@bp.route("/apply/<step_name>", methods=["GET", "POST"])
def step(step_name):
    if step_name not in STEPS or step_name in ("check", "confirmation"):
        return redirect(url_for("main.index"))

    answers = session.get("answers", {})
    errors = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        # Checkboxes won't appear in form_data if unchecked — handle explicitly
        if step_name == "declaration":
            form_data["declaration"] = form_data.get("declaration", "")

        validator = VALIDATORS.get(step_name)
        if validator:
            errors = validator(form_data)

        if not errors:
            for field in FORM_FIELDS.get(step_name, []):
                answers[field] = form_data.get(field, "")
            session["answers"] = answers
            return redirect(url_for("main.step", step_name=next_step(step_name)))

    return render_template(f"steps/{step_name}.html", answers=answers, errors=errors)


@bp.route("/apply/check", methods=["GET", "POST"])
def check():
    answers = session.get("answers", {})
    if not answers:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        ref = str(uuid.uuid4())[:8].upper()
        session["ref"] = ref
        return redirect(url_for("main.confirmation"))
    return render_template("steps/check.html", answers=answers)


@bp.route("/apply/confirmation")
def confirmation():
    ref = session.get("ref")
    if not ref:
        return redirect(url_for("main.index"))
    return render_template("steps/confirmation.html", ref=ref)
