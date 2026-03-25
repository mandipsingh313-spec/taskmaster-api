import pytest
from app import create_app, db


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register and log in a test user, return auth headers."""
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password1",
    })
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "Password1",
    })
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    """Register a second user and return their auth headers."""
    client.post("/api/auth/register", json={
        "username": "otheruser",
        "email": "other@example.com",
        "password": "Password2",
    })
    response = client.post("/api/auth/login", json={
        "email": "other@example.com",
        "password": "Password2",
    })
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
