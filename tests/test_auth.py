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


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user"] = {"type": "referrer", "email": "test@example.com", "name": "Test"}

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Sign in" in response.get_data(as_text=True)

    with client.session_transaction() as sess:
        assert "user" not in sess
