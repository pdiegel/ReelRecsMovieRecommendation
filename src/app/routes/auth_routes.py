import tmdbsimple as tmdb
from flask import redirect, request, url_for
from flask_login import LoginManager, login_user, logout_user

from ...constants.api_constants import TOKEN_AUTH_URL
from ...services.login_service import User


def set_up_auth_routes(app, account: tmdb.Account, login_manager: LoginManager):
    @app.route("/login")
    def login() -> str:
        """
        Route for handling user login.

        The route accepts an optional 'next' parameter in the URL,
        which is the URL of the page the user was trying to access
        before being redirected to the login page.

        After the user logs in, they are redirected back to this
        original page. If no 'next' parameter was provided, they are
        redirected to the homepage.
        """
        auth = tmdb.Authentication()
        request_token = auth.token_new()["request_token"]
        redirect_to = request.args.get("next") + url_for("create_user_session")
        return redirect(
            TOKEN_AUTH_URL.format(
                request_token=request_token,
                redirect_to=redirect_to,
            )
        )

    @app.route("/create_session")
    def create_user_session() -> str:
        """
        Route for creating a user session.

        The route accepts a 'request_token' parameter in the URL, which
        is used to create the session. The route also accepts an
        optional 'next' parameter, which is the URL of the page the user
        was trying to access before being redirected to the login page.

        After the session is created, the user is redirected back to the
        original page. If no 'next' parameter was provided, they are
        redirected to the homepage.
        """
        request_token = request.args.get("request_token")
        auth = tmdb.Authentication()
        user_session = auth.session_new(request_token=request_token)
        session_id = user_session.get("session_id")
        if session_id is not None:
            user = User(session_id)
            login_user(user, remember=True)
            account.session_id = session_id
            account.info()

        return redirect("/")

    @app.route("/logout")
    def logout() -> str:
        logout_user()
        return redirect("/")

    @app.route("/error")
    def error() -> str:
        return redirect("/")

    @login_manager.unauthorized_handler
    def unauthorized() -> str:
        # If the user is not authorized, redirect them to the login
        # page and include the next parameter
        next_url = request.url
        login_url = url_for("login", next=next_url)
        return redirect(login_url)

    @login_manager.user_loader
    def load_user(session_id) -> User:
        return User(session_id)
