import os
from datetime import timedelta

from flask import Flask
from flask_login import LoginManager

from ..constants.api_constants import STATIC_FOLDER, TEMPLATES_FOLDER


def create_app():
    app = Flask(
        __name__,
        template_folder=TEMPLATES_FOLDER,
        static_folder=STATIC_FOLDER,
    )
    app.secret_key = os.urandom(24)
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    login_manager = LoginManager()
    login_manager.init_app(app)

    return app, login_manager


app, login_manager = create_app()
