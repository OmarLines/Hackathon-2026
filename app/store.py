from werkzeug.security import generate_password_hash

# In-memory stores — reset on app restart (fine for hackathon)

# Referrer accounts keyed by email
referrers = {
    "referrer@test.com": {
        "password_hash": generate_password_hash("password"),
        "name": "Demo Referrer",
        "referrals": [],  # list of ref numbers submitted by this referrer
    }
}

# Referee accounts created on form submission, keyed by reference number
# Each entry: { child_name, postcode, answers, referrer_email }
referees = {}

# Referrer details captured on the referral step, keyed by user sub
referrer_details = {}
