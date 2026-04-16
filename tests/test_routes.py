from werkzeug.security import generate_password_hash

from app.store import referrer_details, referrers


def test_index_redirect_to_login(client):
    response = client.get("/", follow_redirects=True)
    assert "Sign in" in response.get_data(as_text=True)


def test_apply_start_requires_auth(client):
    # Ensure no active session
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get("/apply/start", follow_redirects=True)
    assert "Sign in" in response.get_data(as_text=True)


def test_apply_child_step_auth(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.get("/apply/child")
    assert response.status_code == 200
    assert "Child's details" in response.get_data(as_text=True)


def test_apply_child_step_post_success(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "type": "referrer",
            "email": "test@example.com",
            "name": "Test User",
        }

    response = client.post(
        "/apply/child",
        data={
            "child_name": "Test Child",
            "child_dob_day": "01",
            "child_dob_month": "01",
            "child_dob_year": "2020",
            "gender": "Male",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Child's home address" in response.get_data(as_text=True)


def test_apply_child_step_post_validation(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.post(
        "/apply/child",
        data={
            "child_name": "",
            "child_dob_day": "99",
            "child_dob_month": "99",
            "child_dob_year": "2020",
            "gender": "",
        },
    )

    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "Enter the child&#39;s name" in data
    assert "Enter a real date of birth" in data
    assert "Enter the child&#39;s gender" in data


def test_check_page_redirect_if_no_answers(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "type": "referrer",
            "email": "test@example.com",
            "name": "Test User",
        }
        sess.pop("answers", None)

    response = client.get("/apply/check", follow_redirects=True)
    assert response.status_code == 200
    assert "Welcome, Test User" in response.get_data(as_text=True)


def test_referrer_step_prefills_saved_details(client):
    referrers.clear()
    referrer_details.clear()
    referrers["test@example.com"] = {
        "form_access": {"children-centre-services"},
        "name": "Test User",
        "password_hash": generate_password_hash("password123"),
        "referrals": [],
        "sub": "user-123",
    }
    referrer_details["user-123"] = {
        "referrer_name": "Saved Referrer",
        "role_agency": "Saved Agency",
    }

    with client.session_transaction() as sess:
        sess["user"] = {
            "type": "referrer",
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user-123",
        }

    response = client.get("/apply/referrer")

    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'value="Saved Referrer"' in data
    assert 'value="Saved Agency"' in data
    assert 'id="referral_date_today"' in data


def test_referrer_step_post_saves_details(client):
    referrers.clear()
    referrer_details.clear()
    referrers["test@example.com"] = {
        "form_access": {"children-centre-services"},
        "name": "Test User",
        "password_hash": generate_password_hash("password123"),
        "referrals": [],
        "sub": "user-123",
    }

    with client.session_transaction() as sess:
        sess["user"] = {
            "type": "referrer",
            "email": "test@example.com",
            "name": "Test User",
            "sub": "user-123",
        }

    response = client.post(
        "/apply/referrer",
        data={
            "referrer_name": "Jane Example",
            "role_agency": "Health Visitor",
            "referral_date_day": "16",
            "referral_date_month": "4",
            "referral_date_year": "2026",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert referrer_details["user-123"] == {
        "referrer_name": "Jane Example",
        "role_agency": "Health Visitor",
    }
