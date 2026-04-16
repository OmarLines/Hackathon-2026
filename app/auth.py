from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .store import referrers, referees

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user"):
        return redirect(url_for("auth.dashboard"))

    errors = {}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name:
            errors["name"] = "Enter your full name"
        if not email:
            errors["email"] = "Enter your email address"
        elif email in referrers:
            errors["email"] = "An account with this email address already exists"
        if not password:
            errors["password"] = "Enter a password"
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters"
        if not confirm:
            errors["confirm_password"] = "Confirm your password"
        elif password and confirm != password:
            errors["confirm_password"] = "Passwords do not match"

        if not errors:
            referrers[email] = {
                "password_hash": generate_password_hash(password),
                "name": name,
                "referrals": [],
            }
            session["user"] = {"type": "referrer", "email": email, "name": name}
            return redirect(url_for("auth.dashboard"))

    return render_template("register.html", errors=errors, form=request.form if request.method == "POST" else {})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
            referrer = referrers.get(email)
            if referrer and check_password_hash(referrer["password_hash"], password):
                session["user"] = {"type": "referrer", "email": email, "name": referrer["name"]}
                return redirect(url_for("auth.dashboard"))
            errors["referrer_login"] = "Incorrect email address or password"

        elif user_type == "referee":
            ref_number = request.form.get("ref_number", "").strip().upper()
            postcode = request.form.get("postcode", "").strip().upper().replace(" ", "")
            referee = referees.get(ref_number)
            if referee and referee["postcode"].upper().replace(" ", "") == postcode:
                session["user"] = {
                    "type": "referee",
                    "ref_number": ref_number,
                    "name": referee["child_name"],
                }
                return redirect(url_for("auth.dashboard"))
            errors["referee_login"] = "Incorrect reference number or postcode"

    return render_template("login.html", errors=errors, form=request.form if request.method == "POST" else {})


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    if user["type"] == "referrer":
        referrer = referrers.get(user["email"], {})
        submitted = [referees[r] for r in referrer.get("referrals", []) if r in referees]
        return render_template("dashboard_referrer.html", user=user, referrals=submitted)

    referee = referees.get(user["ref_number"], {})
    return render_template("dashboard_referee.html", user=user, referral=referee)
