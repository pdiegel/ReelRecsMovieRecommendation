import os
from datetime import timedelta

import requests
import tmdbsimple as tmdb
from flask import Flask
from flask_login import LoginManager

from src.constants.api_constants import (
    API_HEADERS,
    API_KEY,
)

from src.app.routes.auth_routes import set_up_auth_routes
from src.app.routes.movie_routes import set_up_movie_routes
from src.app.routes.api_routes import set_up_api_routes


def create_app():
    app = Flask(
        __name__,
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

    tmdb.API_KEY = API_KEY
    tmdb.REQUESTS_SESSION = requests.Session()
    tmdb.REQUESTS_SESSION.headers.update(API_HEADERS)

    account = tmdb.Account("")

    set_up_api_routes(app, account)
    set_up_auth_routes(app, account, login_manager)
    set_up_movie_routes(app, account)

    return app, login_manager


app, login_manager = create_app()
