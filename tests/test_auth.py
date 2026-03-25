import pytest


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password1",
        })
        assert response.status_code == 201
        data = response.get_json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"

    def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={
            "username": "newuser",
        })
        assert response.status_code == 400

    def test_register_no_data(self, client):
        response = client.post("/api/auth/register")
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "username": "user1",
            "email": "not-an-email",
            "password": "Password1",
        })
        assert response.status_code == 422

    def test_register_weak_password(self, client):
        response = client.post("/api/auth/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "weak",
        })
        assert response.status_code == 422

    def test_register_password_no_uppercase(self, client):
        response = client.post("/api/auth/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password1",
        })
        assert response.status_code == 422

    def test_register_password_no_number(self, client):
        response = client.post("/api/auth/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "Password",
        })
        assert response.status_code == 422

    def test_register_duplicate_username(self, client):
        client.post("/api/auth/register", json={
            "username": "dupuser",
            "email": "dup1@example.com",
            "password": "Password1",
        })
        response = client.post("/api/auth/register", json={
            "username": "dupuser",
            "email": "dup2@example.com",
            "password": "Password1",
        })
        assert response.status_code == 409

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "username": "user_a",
            "email": "shared@example.com",
            "password": "Password1",
        })
        response = client.post("/api/auth/register", json={
            "username": "user_b",
            "email": "shared@example.com",
            "password": "Password1",
        })
        assert response.status_code == 409

    def test_register_invalid_username_chars(self, client):
        response = client.post("/api/auth/register", json={
            "username": "invalid user!",
            "email": "x@example.com",
            "password": "Password1",
        })
        assert response.status_code == 422

    def test_register_username_too_short(self, client):
        response = client.post("/api/auth/register", json={
            "username": "ab",
            "email": "x@example.com",
            "password": "Password1",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Password1",
        })
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Password1",
        })
        assert response.status_code == 200
        assert "access_token" in response.get_json()

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser2",
            "email": "login2@example.com",
            "password": "Password1",
        })
        response = client.post("/api/auth/login", json={
            "email": "login2@example.com",
            "password": "WrongPass1",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "Password1",
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
        })
        assert response.status_code == 400

    def test_login_no_data(self, client):
        response = client.post("/api/auth/login")
        assert response.status_code == 400


class TestCurrentUser:
    def test_get_me(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert "user" in response.get_json()

    def test_get_me_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401


class TestLogout:
    def test_logout(self, client, auth_headers):
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
