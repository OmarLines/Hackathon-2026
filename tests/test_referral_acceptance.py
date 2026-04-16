from app.store import referees

def test_accept_referral_unauthorized(client):
    response = client.post("/referral/TEST1234/accept", follow_redirects=True)
    assert response.status_code == 403

def test_accept_referral_wrong_user(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referee", "ref_number": "OTHER123"}
    
    response = client.post("/referral/TEST1234/accept", follow_redirects=True)
    assert response.status_code == 403

def test_accept_referral_success(client):
    ref_number = "TEST1234"
    referees[ref_number] = {
        "ref_number": ref_number,
        "postcode_normalized": "SW1A1AA",
        "child_name": "Test Child",
        "status": "sent",
        "answers": {
            "child_name": "Test Child",
            "child_dob_day": "01",
            "child_dob_month": "01",
            "child_dob_year": "2020",
            "gender": "Male",
            "service_type": "prevention",
            "service": "brilliant_babies"
        }
    }
    
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referee", "ref_number": ref_number}
    
    response = client.post(f"/referral/{ref_number}/accept", follow_redirects=True)
    assert response.status_code == 200
    assert referees[ref_number]["status"] == "accepted"
    assert "Accepted" in response.get_data(as_text=True)

def test_create_referral_initial_status(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "type": "referrer",
            "email": "referrer@test.com",
            "name": "Test Referrer"
        }
        sess["answers"] = {
            "child_name": "New Child",
            "postcode": "SW1A 1AA",
            "child_dob_day": "01",
            "child_dob_month": "01",
            "child_dob_year": "2020",
            "gender": "Female"
        }
    
    response = client.post("/apply/check", follow_redirects=True)
    assert response.status_code == 200
    
    # Check the created referral in the store
    import re
    data = response.get_data(as_text=True)
    match = re.search(r"<strong>([A-Z0-9]{8})</strong>", data)
    assert match, "Reference number not found in confirmation page"
    ref_number = match.group(1)
    
    assert referees[ref_number]["status"] == "sent"
