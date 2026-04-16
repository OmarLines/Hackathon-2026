from app.store import referrers


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert "Create a referrer account" in response.get_data(as_text=True)


def test_register_success(client):
    # Clear referrers for clean test
    referrers.clear()

    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Welcome, Test User" in response.get_data(as_text=True)
    assert "test@example.com" in referrers


def test_register_validation(client):
    response = client.post(
        "/register",
        data={
            "name": "",
            "email": "invalid",
            "password": "short",
            "confirm_password": "mismatch",
        },
    )

    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "Enter your full name" in data
    assert "Password must be at least 8 characters" in data
    assert "Passwords do not match" in data


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in" in response.get_data(as_text=True)


def test_admin_login_success(client):
    client.application.config.update(
        {
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "admin",
        }
    )

    response = client.post(
        "/login",
        data={
            "user_type": "admin",
            "admin_username": "admin",
            "admin_password": "admin",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Admin dashboard" in response.get_data(as_text=True)


def test_admin_login_failure_message(client):
    client.application.config.update(
        {
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "admin",
        }
    )

    response = client.post(
        "/login",
        data={
            "user_type": "admin",
            "admin_username": "wrong",
            "admin_password": "wrong",
        },
    )

    assert response.status_code == 200
    assert "Incorrect admin username or password" in response.get_data(as_text=True)


def test_referrer_login_failure_message(client):
    response = client.post(
        "/login",
        data={
            "user_type": "referrer",
            "email": "test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 200
    assert (
        "Either your username and password are incorrect, "
        "or you are not registered with this service."
    ) in response.get_data(as_text=True)


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Sign in" in response.get_data(as_text=True)

    with client.session_transaction() as sess:
        assert "user" not in sess
