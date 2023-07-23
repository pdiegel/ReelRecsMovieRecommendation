from ..app.utils import render_movies
from ..constants.api_constants import (
    POPULAR_MOVIES_URL,
    COOKING_MOVIES_URL,
    GENRE_SEARCH_URL,
    API_HEADERS,
    API_KEY,
    RECOMMENDED_MOVIES_URL,
    RATED_MOVIES_URL,
)
from ..services.login_service import (
    create_session,
    get_response_token,
    User,
    get_session_id,
)
from ..services.movie_service import rate_movie
from flask_login import (
    login_user,
    LoginManager,
    logout_user,
    login_required,
    current_user,
)
from flask import request, redirect, jsonify


def set_up_routes(app, login_manager: LoginManager):
    @app.route("/")
    def home():
        return render_movies(
            POPULAR_MOVIES_URL,
            user_api_url=RATED_MOVIES_URL,
            session_id=get_session_id(),
        )

    @app.route("/cooking-movies")
    def cooking_movies():
        return render_movies(COOKING_MOVIES_URL, title="Popular Cooking Movies")

    @app.route("/action-movies")
    def action_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Action Movies", genres=28
        )

    @app.route("/adventure-movies")
    def adventure_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Adventure Movies", genres=12
        )

    @app.route("/comedy-movies")
    def comedy_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Comedy Movies", genres=35
        )

    @app.route("/horror-movies")
    def horror_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Horror Movies", genres=27
        )

    @app.route("/animation-movies")
    def animation_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Animation Movies", genres=16
        )

    @app.route("/crime-movies")
    def crime_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Crime Movies", genres=80
        )

    @app.route("/documentary-movies")
    def documentary_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Documentary Movies", genres=99
        )

    @app.route("/drama-movies")
    def drama_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Drama Movies", genres=18
        )

    @app.route("/family-movies")
    def family_movies():
        return render_movies(
            GENRE_SEARCH_URL, title="Popular Family Movies", genres=10751
        )

    @app.route("/login")
    def login():
        token, redirect = get_response_token(API_HEADERS, API_KEY)
        print("token = " + token)
        return redirect

    @app.route("/create_session")
    def session():
        request_token = request.args.get("request_token")
        session = create_session(request_token, API_HEADERS, API_KEY)
        session_id = session.get("session_id")
        if session_id is not None:
            user = User(session_id)
            login_user(user, remember=True)
            print(user)
            print("session_id = " + session_id)
        return redirect("/")

    @login_manager.user_loader
    def load_user(session_id):
        return User(session_id)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect("/")

    @app.route("/error")
    def error():
        return redirect("/")

    @app.route("/rate_movie/", methods=["POST"])
    @login_required
    def rate():
        print("rate_movie")
        data = request.get_json()
        movie_id = data["movie_id"]
        rating = data["rating"]
        print(f"rating = {rating}")

        try:
            rate_movie(movie_id, rating, current_user.id, API_HEADERS, API_KEY)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))

    @app.route("/api/logged_in", methods=["GET"])
    def logged_in():
        print(current_user.is_authenticated)
        return {"logged_in": current_user.is_authenticated}

    @app.route("/recommended-movies")
    @login_required
    def recommended_movies():
        session_id = get_session_id()
        print(session_id)
        return render_movies(
            RECOMMENDED_MOVIES_URL,
            title="Recommended Movies",
            session_id=session_id,
        )
