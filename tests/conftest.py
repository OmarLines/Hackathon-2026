import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True, "SECRET_KEY": "test-secret"})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clear_store():
    from app.store import referees, referrers

    referees.clear()
    referrers.clear()
    # Re-add default referrers used in tests
    from werkzeug.security import generate_password_hash

    # Standard test users
    for email in ["referrer@test.com", "test@example.com"]:
        referrers[email] = {
            "password_hash": generate_password_hash("password"),
            "name": "Test User",
            "referrals": [],
        }
