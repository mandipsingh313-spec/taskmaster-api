from app.validators import (validate_email, validate_password,
                            validate_username, validate_task_input)


class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is None

    def test_empty_email(self):
        assert validate_email("") is not None

    def test_none_email(self):
        assert validate_email(None) is not None

    def test_missing_at(self):
        assert validate_email("userexample.com") is not None

    def test_missing_domain(self):
        assert validate_email("user@") is not None

    def test_too_long(self):
        assert validate_email("a" * 120 + "@example.com") is not None


class TestValidatePassword:
    def test_valid_password(self):
        assert validate_password("Password1") is None

    def test_too_short(self):
        assert validate_password("Pass1") is not None

    def test_no_uppercase(self):
        assert validate_password("password1") is not None

    def test_no_number(self):
        assert validate_password("Password") is not None

    def test_empty(self):
        assert validate_password("") is not None

    def test_none(self):
        assert validate_password(None) is not None


class TestValidateUsername:
    def test_valid_username(self):
        assert validate_username("valid_user123") is None

    def test_too_short(self):
        assert validate_username("ab") is not None

    def test_special_chars(self):
        assert validate_username("user!name") is not None

    def test_spaces(self):
        assert validate_username("user name") is not None

    def test_empty(self):
        assert validate_username("") is not None

    def test_none(self):
        assert validate_username(None) is not None


class TestValidateTaskInput:
    def test_valid_task(self):
        assert validate_task_input({"title": "My Task"}) is None

    def test_missing_title(self):
        assert validate_task_input({}) is not None

    def test_empty_title(self):
        assert validate_task_input({"title": "  "}) is not None

    def test_invalid_status(self):
        assert validate_task_input({"title": "T", "status": "done"}) is not None

    def test_invalid_priority(self):
        assert validate_task_input({"title": "T", "priority": "urgent"}) is not None

    def test_description_too_long(self):
        assert validate_task_input({"title": "T",
                                    "description": "x" * 5001}) is not None

    def test_all_valid_statuses(self):
        for s in ["pending", "in_progress", "completed", "cancelled"]:
            assert validate_task_input({"title": "T", "status": s}) is None

    def test_all_valid_priorities(self):
        for p in ["low", "medium", "high"]:
            assert validate_task_input({"title": "T", "priority": p}) is None
