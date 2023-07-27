import tmdbsimple as tmdb
from flask import jsonify, redirect, request, session, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from ..app.utils import handle_movie_route
from ..constants.api_constants import (
    ACCOUNT_OBJECT_ID,
    API_ACCESS_TOKEN,
    API_HEADERS,
    API_KEY,
    COOKING_MOVIES_URL,
    GENRE_SEARCH_URL,
    IN_THEATERS_URL,
    POPULAR_MOVIES_URL,
    RATED_MOVIES_URL,
    RECOMMENDED_MOVIES_URL,
    SEARCH_URL,
    SIMILAR_TO_MOVIE_ID_URL,
    TOP_RATED_URL,
    UPCOMING_URL,
    WATCHLIST_URL,
    TOKEN_AUTH_URL,
)
from ..services.login_service import (
    User,
    create_session,
    get_session_id,
    login_to_tmdb,
)
from ..services.movie_service import (
    rate_movie,
    watchlist_movie,
    render_movie_template,
)


def set_up_routes(app, login_manager: LoginManager, account: tmdb.Account):
    @app.route("/")
    def home() -> str:
        session_id = get_session_id()
        popular_movies = tmdb.Movies().popular
        logged_in = current_user.is_authenticated
        return render_movie_template(
            "Popular Movies", session_id, popular_movies, logged_in=logged_in
        )

    @app.route("/cooking-movies")
    def cooking_movies() -> str:
        return handle_movie_route(
            COOKING_MOVIES_URL,
            "Popular Cooking Movies",
            get_session_id(),
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

        return handle_movie_route(
            GENRE_SEARCH_URL,
            f"Popular {genre.capitalize()} Movies",
            get_session_id(),
            genres=genre_id,
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
        # session["next"] = request.args.get("next")
        auth = tmdb.Authentication()
        request_token = auth.token_new()["request_token"]
        return redirect(
            TOKEN_AUTH_URL.format(request_token=request_token, next=next)
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
        data = request.get_json()
        movie_id = data["movie_id"]
        rating = data["rating"]

        try:
            rate_movie(movie_id, rating, current_user.id, API_HEADERS, API_KEY)
            print("successfully rated movie")
            return jsonify(success=True)
        except Exception as e:
            print(f"error rating movie: {e}")
            return jsonify(success=False, error=str(e))

    @app.route("/watchlist_movie/", methods=["POST"])
    @login_required
    def watchlist():
        data = request.get_json()
        movie_id = data.get("movie_id", None)
        watchlist = data.get("watchlist", True)

        try:
            account.watchlist(
                media_type="movie", media_id=movie_id, watchlist=watchlist
            )
            return jsonify(success=True)
        except Exception as e:
            print(f"error adding movie to watchlist: {e}")
            return jsonify(success=False, error=str(e))

    @app.route("/recommendations")
    @login_required
    def recommended_movies() -> str:
        return handle_movie_route(
            RECOMMENDED_MOVIES_URL,
            "Recommended Movies",
            get_session_id(),
        )

    @app.route("/rated-movies")
    @login_required
    def rated() -> str:
        return handle_movie_route(
            RATED_MOVIES_URL,
            "My Ratings",
            get_session_id(),
        )

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

    @app.route("/search", methods=["GET"])
    def search() -> str:
        query = request.args.get("query")
        return handle_movie_route(
            SEARCH_URL,
            f'Results for "{query}"',
            get_session_id(),
            query=query,
        )

    @app.route("/in-theaters")
    def in_theaters():
        return handle_movie_route(
            IN_THEATERS_URL,
            "In Theaters",
            get_session_id(),
        )

    @app.route("/top-rated")
    def top_rated():
        return handle_movie_route(
            TOP_RATED_URL,
            "Top Rated Movies",
            get_session_id(),
        )

    @app.route("/upcoming-movies")
    def upcoming_movies():
        return handle_movie_route(
            UPCOMING_URL,
            "Upcoming Movies",
            get_session_id(),
        )

    @app.route("/watchlist-movies")
    @login_required
    def watchlist_movies():
        logged_in = current_user.is_authenticated
        watchlist = account.watchlist_movies
        return render_movie_template(
            "My Watchlist",
            get_session_id(),
            watchlist,
            pages=-1,
            logged_in=logged_in,
        )

    @app.route("/similar-movies/<movie_id>/")
    def similar_movies(movie_id: str) -> str:
        movie_title = request.args.get("title")
        return handle_movie_route(
            SIMILAR_TO_MOVIE_ID_URL,
            "Movies Similar to " + movie_title,
            get_session_id(),
            movie_id=movie_id,
            include_adult="false",
        )
