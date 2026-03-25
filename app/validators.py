import re


def validate_email(email):
    if not email:
        return "Email is required"
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not re.match(pattern, email):
        return "Invalid email format"
    if len(email) > 120:
        return "Email must be 120 characters or fewer"
    return None


def validate_password(password):
    if not password:
        return "Password is required"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if len(password) > 128:
        return "Password must be 128 characters or fewer"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    return None


def validate_username(username):
    if not username:
        return "Username is required"
    if len(username) < 3:
        return "Username must be at least 3 characters"
    if len(username) > 80:
        return "Username must be 80 characters or fewer"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers and underscores"
    return None


def validate_task_input(data):
    title = data.get("title", "")
    if not title or not title.strip():
        return "Task title is required"
    if len(title.strip()) > 200:
        return "Title must be 200 characters or fewer"

    status = data.get("status", "pending")
    valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        return f"Invalid status. Must be one of {valid_statuses}"

    priority = data.get("priority", "medium")
    valid_priorities = ["low", "medium", "high"]
    if priority not in valid_priorities:
        return f"Invalid priority. Must be one of {valid_priorities}"

    description = data.get("description", "")
    if description and len(description) > 5000:
        return "Description must be 5000 characters or fewer"

    return None
