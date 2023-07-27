import tmdbsimple as tmdb
from flask import jsonify, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from ..app.utils import handle_movie_route
from ..constants.api_constants import (
    API_ACCESS_TOKEN,
    API_HEADERS,
    API_KEY,
    GENRE_SEARCH_URL,
    RECOMMENDED_MOVIES_URL,
    TOKEN_AUTH_URL,
)
from ..services.login_service import User, get_session_id
from ..services.movie_service import rate_movie, render_movie_template


def set_up_routes(app, login_manager: LoginManager, account: tmdb.Account):
    GENRES = {
        "action": 28,
        "adventure": 12,
        "animation": 16,
        "comedy": 35,
        "crime": 80,
        "documentary": 99,
        "drama": 18,
        "family": 10751,
        "fantasy": 14,
        "history": 36,
        "horror": 27,
        "music": 10402,
        "mystery": 9648,
        "romance": 10749,
        "science fiction": 878,
    }

    @app.route("/")
    def home() -> str:
        session_id = get_session_id()
        popular_movies = tmdb.Movies().popular
        logged_in = current_user.is_authenticated
        return render_movie_template(
            "Popular Movies",
            account,
            popular_movies,
            logged_in=logged_in,
        )

    @app.route("/cooking-movies")
    def cooking_movies() -> str:
        logged_in = current_user.is_authenticated
        func = tmdb.Discover().movie
        keywords = "18293|6808|10637"
        return render_movie_template(
            "Cooking Movies",
            account,
            func,
            pages=-1,
            logged_in=logged_in,
            with_keywords=keywords,
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
        logged_in = current_user.is_authenticated
        func = tmdb.Discover().movie
        genre_id = GENRES.get(genre)
        if genre_id is None:
            return redirect("/error")

        return render_movie_template(
            f"Popular {genre.capitalize()} Movies",
            account,
            func,
            with_genres=genre_id,
            logged_in=logged_in,
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

    @app.route("/favorite_movie/", methods=["POST"])
    @login_required
    def favorite():
        data = request.get_json()
        movie_id = data.get("movie_id", None)
        favorite = data.get("favorite", True)

        try:
            account.favorite(
                media_type="movie", media_id=movie_id, favorite=favorite
            )
            return jsonify(success=True)
        except Exception as e:
            print(f"error adding movie to favorites: {e}")
            return jsonify(success=False, error=str(e))

    @app.route("/recommendations")
    @login_required
    def recommended_movies() -> str:
        logged_in = current_user.is_authenticated
        movies = handle_movie_route(RECOMMENDED_MOVIES_URL, get_session_id())
        return render_movie_template(
            "Recommended Movies",
            account,
            movies=movies,
            logged_in=logged_in,
        )

    @app.route("/rated-movies")
    @login_required
    def rated() -> str:
        logged_in = current_user.is_authenticated
        func = account.rated_movies
        return render_movie_template(
            "My Ratings",
            account,
            func,
            logged_in=logged_in,
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
        logged_in = current_user.is_authenticated
        func = tmdb.Search().movie
        return render_movie_template(
            "Results for " + query,
            account,
            func,
            logged_in=logged_in,
            query=query,
        )

    @app.route("/in-theaters")
    def in_theaters():
        logged_in = current_user.is_authenticated
        func = tmdb.Movies().now_playing
        return render_movie_template(
            "In Theaters Now",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/top-rated")
    def top_rated():
        logged_in = current_user.is_authenticated
        func = tmdb.Movies().top_rated
        return render_movie_template(
            "Top Rated Movies",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/upcoming-movies")
    def upcoming_movies():
        logged_in = current_user.is_authenticated
        func = tmdb.Movies().upcoming
        return render_movie_template(
            "Upcoming Movies",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/watchlist-movies")
    @login_required
    def watchlist_movies():
        logged_in = current_user.is_authenticated
        func = account.watchlist_movies
        return render_movie_template(
            "My Watchlist",
            account,
            func,
            pages=-1,
            logged_in=logged_in,
        )

    @app.route("/similar-movies/<movie_id>/")
    def similar_movies(movie_id: str) -> str:
        logged_in = current_user.is_authenticated
        movie_title = request.args.get("title")
        func = tmdb.Movies(movie_id).similar_movies
        return render_movie_template(
            "Movies Similar to " + movie_title,
            account,
            func,
            logged_in=logged_in,
        )
