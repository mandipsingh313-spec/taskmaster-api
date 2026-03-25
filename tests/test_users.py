class TestUserProfile:
    def test_get_profile(self, client, auth_headers):
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == 200
        assert "user" in response.get_json()

    def test_get_profile_unauthorized(self, client):
        response = client.get("/api/users/profile")
        assert response.status_code == 401

    def test_update_profile_email(self, client, auth_headers):
        response = client.put("/api/users/profile", headers=auth_headers,
                               json={"email": "updated@example.com"})
        assert response.status_code == 200
        assert response.get_json()["user"]["email"] == "updated@example.com"

    def test_update_profile_invalid_email(self, client, auth_headers):
        response = client.put("/api/users/profile", headers=auth_headers,
                               json={"email": "not-an-email"})
        assert response.status_code == 422

    def test_update_profile_duplicate_email(self, client, auth_headers,
                                             second_user_headers):
        response = client.put("/api/users/profile", headers=auth_headers,
                               json={"email": "other@example.com"})
        assert response.status_code == 409

    def test_update_profile_no_data(self, client, auth_headers):
        response = client.put("/api/users/profile", headers=auth_headers)
        assert response.status_code == 400


class TestChangePassword:
    def test_change_password_success(self, client, auth_headers):
        response = client.post("/api/users/change-password",
                                headers=auth_headers,
                                json={"current_password": "Password1",
                                      "new_password": "NewPassword2"})
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        response = client.post("/api/users/change-password",
                                headers=auth_headers,
                                json={"current_password": "WrongPass1",
                                      "new_password": "NewPassword2"})
        assert response.status_code == 401

    def test_change_password_weak_new(self, client, auth_headers):
        response = client.post("/api/users/change-password",
                                headers=auth_headers,
                                json={"current_password": "Password1",
                                      "new_password": "weak"})
        assert response.status_code == 422

    def test_change_password_missing_fields(self, client, auth_headers):
        response = client.post("/api/users/change-password",
                                headers=auth_headers,
                                json={"current_password": "Password1"})
        assert response.status_code == 400

    def test_change_password_no_data(self, client, auth_headers):
        response = client.post("/api/users/change-password",
                                headers=auth_headers)
        assert response.status_code == 400


class TestDeactivate:
    def test_deactivate_account(self, client, auth_headers):
        response = client.post("/api/users/deactivate", headers=auth_headers)
        assert response.status_code == 200

    def test_deactivate_blocks_login(self, client, auth_headers):
        client.post("/api/users/deactivate", headers=auth_headers)
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "Password1",
        })
        assert response.status_code == 403
