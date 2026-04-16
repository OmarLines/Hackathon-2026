from flask import Flask
from .routes import bp
from .auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-change-in-production"
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp)
    return app
