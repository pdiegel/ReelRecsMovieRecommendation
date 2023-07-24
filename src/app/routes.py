from flask import jsonify, redirect, request, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from ..app.utils import fetch_movies, fetch_rated_movies, render_movies_page
from ..constants.api_constants import (
    API_HEADERS,
    API_KEY,
    COOKING_MOVIES_URL,
    GENRE_SEARCH_URL,
    POPULAR_MOVIES_URL,
    RATED_MOVIES_URL,
    RECOMMENDED_MOVIES_URL,
    API_ACCESS_TOKEN,
)
from ..services.login_service import (
    User,
    create_session,
    get_response_token,
    get_session_id,
)
from ..services.movie_service import rate_movie

GENRE_IDS = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "horror": 27,
}


def set_up_routes(app, login_manager: LoginManager):
    @app.route("/")
    def home() -> str:
        session_id = get_session_id()
        movies = fetch_movies(POPULAR_MOVIES_URL, session_id=session_id)
        rated_movies = fetch_rated_movies(
            RATED_MOVIES_URL, API_HEADERS, session_id
        )
        return render_movies_page(movies, "Popular Movies", rated_movies)

    @app.route("/cooking-movies")
    def cooking_movies() -> str:
        session_id = get_session_id()
        movies = fetch_movies(COOKING_MOVIES_URL, session_id=session_id)
        rated_movies = fetch_rated_movies(
            RATED_MOVIES_URL, API_HEADERS, session_id
        )
        return render_movies_page(
            movies, "Popular Cooking Movies", rated_movies
        )

    @app.route("/<genre>-movies")
    def genre_movies(genre: str) -> str:
        """
        Route for displaying movies of a specific genre.

        Args:
            genre (str): The genre of movies to display. This is taken
                from the URL.

        Returns:
            A rendered template displaying the movies of the specified
            genre. If the genre is not found, the user is redirected
            to an error page.
        """
        genre_id = GENRE_IDS.get(genre)
        if genre_id is None:
            return redirect("/error")
        session_id = get_session_id()
        movies = fetch_movies(
            GENRE_SEARCH_URL,
            session_id=session_id,
            genres=genre_id,
        )
        rated_movies = fetch_rated_movies(
            RATED_MOVIES_URL, API_HEADERS, session_id
        )
        return render_movies_page(
            movies, f"Popular {genre.capitalize()} Movies", rated_movies
        )

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
        session["next"] = request.args.get("next")
        token, redirect = get_response_token(
            API_HEADERS, API_KEY, next=session["next"]
        )
        return redirect

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
        next_page = request.args.get("next")
        user_session = create_session(request_token, API_HEADERS, API_KEY)
        session_id = user_session.get("session_id")
        if session_id is not None:
            user = User(session_id)
            login_user(user, remember=True)

        if not next_page:
            next_page = url_for("home")
        return redirect(next_page)

    @login_manager.user_loader
    def load_user(session_id) -> User:
        return User(session_id)

    @app.route("/logout")
    def logout() -> str:
        logout_user()
        return redirect("/")

    @app.route("/error")
    def error() -> str:
        return redirect("/")

    @app.route("/rate_movie/", methods=["POST"])
    @login_required
    def rate() -> str:
        print("rate_movie")
        data = request.get_json()
        movie_id = data["movie_id"]
        rating = data["rating"]
        print(f"movie_id = {movie_id}")
        print(f"rating = {rating}")

        try:
            rate_movie(movie_id, rating, current_user.id, API_HEADERS, API_KEY)
            print("successfully rated movie")
            return jsonify(success=True)
        except Exception as e:
            print(f"error rating movie: {e}")
            return jsonify(success=False, error=str(e))

    @app.route("/recommendations")
    @login_required
    def recommended_movies() -> str:
        session_id = get_session_id()
        movies = fetch_movies(
            RECOMMENDED_MOVIES_URL,
            session_id=session_id,
        )
        rated_movies = fetch_rated_movies(
            RATED_MOVIES_URL, API_HEADERS, session_id
        )
        return render_movies_page(movies, "Recommended Movies", rated_movies)

    @app.route("/rated-movies")
    @login_required
    def rated() -> str:
        session_id = get_session_id()
        movies = fetch_movies(
            RATED_MOVIES_URL,
            session_id=session_id,
        )
        rated_movies = fetch_rated_movies(
            RATED_MOVIES_URL, API_HEADERS, session_id
        )
        return render_movies_page(movies, "My Ratings", rated_movies)

    @login_manager.unauthorized_handler
    def unauthorized() -> str:
        # If the user is not authorized, redirect them to the login
        # page and include the next parameter
        next_url = request.url
        login_url = url_for("login", next=next_url)
        return redirect(login_url)

    @app.route("/api/logged_in", methods=["GET"])
    def logged_in() -> str:
        print(current_user.is_authenticated)
        return {"logged_in": current_user.is_authenticated}

    @app.route("/api/session_id", methods=["GET"])
    @login_required
    def current_session() -> str:
        session_id = get_session_id()
        return {"session_id": session_id}

    @app.route("/api/token", methods=["GET"])
    def access_token() -> str:
        return {"access_token": API_ACCESS_TOKEN}
