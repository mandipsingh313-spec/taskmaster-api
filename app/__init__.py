from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///taskmaster.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    if config:
        app.config.update(config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.auth import auth_bp
    from app.tasks import tasks_bp
    from app.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    with app.app_context():
        db.create_all()

    return app
