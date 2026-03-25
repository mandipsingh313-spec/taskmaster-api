from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Task, TaskComment, User
from app.validators import validate_task_input
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()

    status = request.args.get("status")
    priority = request.args.get("priority")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if per_page > 100:
        per_page = 100

    query = Task.query.filter_by(user_id=user_id)

    if status:
        if status not in Task.VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of {Task.VALID_STATUSES}"}), 422
        query = query.filter_by(status=status)

    if priority:
        if priority not in Task.VALID_PRIORITIES:
            return jsonify({"error": f"Invalid priority. Must be one of {Task.VALID_PRIORITIES}"}), 422
        query = query.filter_by(priority=priority)

    query = query.order_by(Task.created_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "tasks": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": page,
        "per_page": per_page,
    }), 200


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.route("/", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    err = validate_task_input(data)
    if err:
        return jsonify({"error": err}), 422

    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"])
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use ISO 8601"}), 422

    task = Task(
        title=data["title"].strip(),
        description=data.get("description", "").strip(),
        status=data.get("status", "pending"),
        priority=data.get("priority", "medium"),
        due_date=due_date,
        user_id=user_id,
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": task.to_dict(),
    }), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data:
        if not data["title"] or not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 422
        task.title = data["title"].strip()

    if "description" in data:
        task.description = data["description"].strip()

    if "status" in data:
        if data["status"] not in Task.VALID_STATUSES:
            return jsonify({"error": f"Invalid status"}), 422
        task.status = data["status"]

    if "priority" in data:
        if data["priority"] not in Task.VALID_PRIORITIES:
            return jsonify({"error": "Invalid priority"}), 422
        task.priority = data["priority"]

    if "due_date" in data:
        if data["due_date"] is None:
            task.due_date = None
        else:
            try:
                task.due_date = datetime.fromisoformat(data["due_date"])
            except ValueError:
                return jsonify({"error": "Invalid due_date format"}), 422

    task.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": task.to_dict(),
    }), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200


@tasks_bp.route("/<int:task_id>/complete", methods=["PATCH"])
@jwt_required()
def complete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.status = "completed"
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Task marked as completed",
        "task": task.to_dict(),
    }), 200


@tasks_bp.route("/<int:task_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    comments = TaskComment.query.filter_by(task_id=task_id).all()
    return jsonify({
        "comments": [c.to_dict() for c in comments]
    }), 200


@tasks_bp.route("/<int:task_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data or not data.get("content", "").strip():
        return jsonify({"error": "Comment content is required"}), 400

    comment = TaskComment(
        content=data["content"].strip(),
        task_id=task_id,
        user_id=user_id,
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added successfully",
        "comment": comment.to_dict(),
    }), 201


@tasks_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()

    total = Task.query.filter_by(user_id=user_id).count()
    pending = Task.query.filter_by(user_id=user_id, status="pending").count()
    in_progress = Task.query.filter_by(user_id=user_id, status="in_progress").count()
    completed = Task.query.filter_by(user_id=user_id, status="completed").count()
    cancelled = Task.query.filter_by(user_id=user_id, status="cancelled").count()

    high = Task.query.filter_by(user_id=user_id, priority="high").count()
    medium = Task.query.filter_by(user_id=user_id, priority="medium").count()
    low = Task.query.filter_by(user_id=user_id, priority="low").count()

    completion_rate = (completed / total * 100) if total > 0 else 0

    return jsonify({
        "total_tasks": total,
        "by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
        },
        "by_priority": {
            "high": high,
            "medium": medium,
            "low": low,
        },
        "completion_rate": round(completion_rate, 2),
    }), 200
