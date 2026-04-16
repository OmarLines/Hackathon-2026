import uuid
from werkzeug.security import generate_password_hash

# Demo constants
DEMO_REFERRER_EMAIL = "referrer@test.com"
DEMO_REFERRER_SUB = str(
    uuid.uuid5(uuid.NAMESPACE_URL, f"local-referrer:{DEMO_REFERRER_EMAIL}")
)

# Referrer accounts keyed by email
referrers_data = {
    DEMO_REFERRER_EMAIL: {
        "password_hash": generate_password_hash("password"),
        "name": "Demo Referrer",
        "referrals": ["REF12345", "REF67890", "REFABCDE"],
        "sub": DEMO_REFERRER_SUB,
        "form_access": {"children-centre-services"},
    }
}

# Referee accounts keyed by reference number
referees_data = {
    "REF12345": {
        "ref_number": "REF12345",
        "child_name": "James Smith",
        "postcode": "NE1 1AA",
        "postcode_normalized": "NE11AA",
        "status": "accepted",
        "created_at": "2026-04-01T10:00:00Z",
        "referrer_email": DEMO_REFERRER_EMAIL,
        "referrer_name": "Demo Referrer",
        "user_id": DEMO_REFERRER_SUB,
        "answers": {
            "child_name": "James Smith",
            "child_dob_day": "15",
            "child_dob_month": "05",
            "child_dob_year": "2023",
            "gender": "Male",
            "address_line1": "1 High Street",
            "town": "Newcastle",
            "postcode": "NE1 1AA",
            "tel_no": "0191 123 4567",
            "parent_name": "Sarah Smith",
            "parent_email": "sarah@example.com",
            "service_type": "prevention",
            "service": "brilliant_babies",
            "registered_sure_start": "yes",
            "verbal_consent": "yes",
        },
    },
    "REF67890": {
        "ref_number": "REF67890",
        "child_name": "Emily Brown",
        "postcode": "NE2 2BB",
        "postcode_normalized": "NE22BB",
        "status": "sent",
        "created_at": "2026-04-10T14:30:00Z",
        "referrer_email": DEMO_REFERRER_EMAIL,
        "referrer_name": "Demo Referrer",
        "user_id": DEMO_REFERRER_SUB,
        "answers": {
            "child_name": "Emily Brown",
            "child_dob_day": "22",
            "child_dob_month": "11",
            "child_dob_year": "2022",
            "gender": "Female",
            "address_line1": "22 Low Road",
            "town": "Gosforth",
            "postcode": "NE2 2BB",
            "tel_no": "0191 765 4321",
            "parent_name": "Mark Brown",
            "parent_email": "mark@example.com",
            "service_type": "intervention",
            "service": "henry",
            "registered_sure_start": "yes",
            "verbal_consent": "yes",
        },
    },
    "REFABCDE": {
        "ref_number": "REFABCDE",
        "child_name": "Noah Wilson",
        "postcode": "NE3 3CC",
        "postcode_normalized": "NE33CC",
        "status": "sent",
        "created_at": "2026-04-15T09:15:00Z",
        "referrer_email": DEMO_REFERRER_EMAIL,
        "referrer_name": "Demo Referrer",
        "user_id": DEMO_REFERRER_SUB,
        "answers": {
            "child_name": "Noah Wilson",
            "child_dob_day": "03",
            "child_dob_month": "01",
            "child_dob_year": "2024",
            "gender": "Male",
            "address_line1": "33 Middle Way",
            "town": "Jesmond",
            "postcode": "NE3 3CC",
            "tel_no": "0191 999 8888",
            "parent_name": "Alice Wilson",
            "parent_email": "alice@example.com",
            "service_type": "prevention",
            "service": "tiny_talkers",
            "registered_sure_start": "yes",
            "verbal_consent": "yes",
        },
    },
}
