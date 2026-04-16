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
