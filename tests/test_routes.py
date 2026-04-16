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
            "child_dob": "2020-01-01",
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
            "child_dob": "",
            "gender": "",
        },
    )

    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "Enter the child&#39;s name" in data
    assert "Enter the child&#39;s date of birth" in data
    assert "Enter the child&#39;s gender" in data


def test_apply_child_step_post_future_date(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.post(
        "/apply/child",
        data={
            "child_name": "Test Child",
            "child_dob": "2099-01-01",
            "gender": "Male",
        },
    )

    assert response.status_code == 200
    assert "Date of birth must be in the past" in response.get_data(as_text=True)


def test_apply_child_step_post_invalid_date(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.post(
        "/apply/child",
        data={
            "child_name": "Test Child",
            "child_dob": "not-a-date",
            "gender": "Male",
        },
    )

    assert response.status_code == 200
    assert "Enter a real date of birth" in response.get_data(as_text=True)


def test_apply_parent_step_post_success(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/parent",
        data={
            "parent_name": "Jane Doe",
            "parent_email": "jane@example.com",
            "parent_dob": "1985-06-14",
            "family_tel": "",
            "locality": "Southwark",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Referrer details" in response.get_data(as_text=True)


def test_apply_parent_step_post_missing_required_fields(client):
    """Email and DOB are now required — omitting them should fail validation."""
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/parent",
        data={
            "parent_name": "Jane Doe",
            "parent_email": "",
            "parent_dob": "",
            "family_tel": "",
            "locality": "Southwark",
        },
    )

    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "Enter the parent or carer&#39;s email address" in data
    assert "Enter the parent or carer&#39;s date of birth" in data


def test_apply_parent_step_post_invalid_email(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/parent",
        data={
            "parent_name": "Jane Doe",
            "parent_email": "not-an-email",
            "parent_dob": "1985-06-14",
            "family_tel": "",
            "locality": "Southwark",
        },
    )

    assert response.status_code == 200
    assert "Enter a real email address" in response.get_data(as_text=True)


def test_apply_parent_step_post_future_dob(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/parent",
        data={
            "parent_name": "Jane Doe",
            "parent_email": "",
            "parent_dob": "2099-01-01",
            "family_tel": "",
            "locality": "Southwark",
        },
    )

    assert response.status_code == 200
    assert "Date of birth must be in the past" in response.get_data(as_text=True)


def test_apply_parent_step_post_invalid_dob(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/parent",
        data={
            "parent_name": "Jane Doe",
            "parent_email": "",
            "parent_dob": "not-a-date",
            "family_tel": "",
            "locality": "Southwark",
        },
    )

    assert response.status_code == 200
    assert "Enter a real date of birth" in response.get_data(as_text=True)


def test_apply_referrer_step_post_success(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/referrer",
        data={
            "referrer_name": "John Smith",
            "role_agency": "Social Worker – Southwark Council",
            "referral_date": "2026-04-16",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Which type of service" in response.get_data(as_text=True)


def test_apply_referrer_step_post_missing_date(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/referrer",
        data={
            "referrer_name": "John Smith",
            "role_agency": "Social Worker",
            "referral_date": "",
        },
    )

    assert response.status_code == 200
    assert "Enter the date of referral" in response.get_data(as_text=True)


def test_apply_referrer_step_post_future_date(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/referrer",
        data={
            "referrer_name": "John Smith",
            "role_agency": "Social Worker",
            "referral_date": "2099-01-01",
        },
    )

    assert response.status_code == 200
    assert "Date of referral must be in the past" in response.get_data(as_text=True)


def test_apply_referrer_step_post_invalid_date(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}
        sess["answers"] = {}

    response = client.post(
        "/apply/referrer",
        data={
            "referrer_name": "John Smith",
            "role_agency": "Social Worker",
            "referral_date": "not-a-date",
        },
    )

    assert response.status_code == 200
    assert "Enter a real date of referral" in response.get_data(as_text=True)


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
