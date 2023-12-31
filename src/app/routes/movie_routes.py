import tmdbsimple as tmdb
from flask import redirect, request
from flask_login import current_user, login_required

from ...constants.api_constants import RECOMMENDED_MOVIES_URL, API_HEADERS
from ...services.login_service import get_session_id
from ...services.movie_service import (
    aggregate_pages,
    render_template_page,
)
import requests

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


def set_up_movie_routes(
    app,
    account: tmdb.Account,
):
    @app.route("/")
    def home() -> str:
        func = tmdb.Movies().popular
        logged_in = current_user.is_authenticated
        return render_template_page(
            "Popular Movies",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/cooking-movies")
    def cooking_movies() -> str:
        logged_in = current_user.is_authenticated
        func = tmdb.Discover().movie
        keywords = "18293|6808|10637"
        return render_template_page(
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

        return render_template_page(
            f"Popular {genre.capitalize()} Movies",
            account,
            func,
            logged_in=logged_in,
            with_genres=genre_id,
        )

    @app.route("/recommendations")
    @login_required
    def recommended_movies() -> str:
        logged_in = current_user.is_authenticated
        func = requests.get
        movies = aggregate_pages(
            pages=5,
            func=func,
            url=RECOMMENDED_MOVIES_URL,
            session_id=get_session_id(),
            headers=API_HEADERS,
        )
        return render_template_page(
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
        return render_template_page(
            "My Ratings",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/search", methods=["GET"])
    def search() -> str:
        query = request.args.get("query")
        logged_in = current_user.is_authenticated
        func = tmdb.Search().movie
        return render_template_page(
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
        return render_template_page(
            "In Theaters Now",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/top-rated")
    def top_rated():
        logged_in = current_user.is_authenticated
        func = tmdb.Movies().top_rated
        return render_template_page(
            "Top Rated Movies",
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/upcoming-movies")
    def upcoming_movies():
        logged_in = current_user.is_authenticated
        func = tmdb.Movies().upcoming
        return render_template_page(
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
        return render_template_page(
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
        return render_template_page(
            "Movies Similar to " + movie_title,
            account,
            func,
            logged_in=logged_in,
        )

    @app.route("/movie/<movie_id>/")
    def movie_page(movie_id: str) -> str:
        logged_in = current_user.is_authenticated
        movie = tmdb.Movies(movie_id)
        movies = movie.info()
        cast = movie.credits()
        media = movie.videos()
        return render_template_page(
            "",
            account,
            movies=movies,
            template_name="movie_details.html",
            pages=1,
            logged_in=logged_in,
            movie_cast=cast,
            media_items=media,
        )

    @app.route("/person/<person_id>/")
    def person_page(person_id: str) -> str:
        logged_in = current_user.is_authenticated
        person = tmdb.People(person_id)
        info = person.info()
        portraits = person.images()
        tagged_images = person.tagged_images()
        movie_credits = person.movie_credits()

        return render_template_page(
            "",
            account,
            template_name="person_details.html",
            pages=1,
            logged_in=logged_in,
            person_info=info,
            person_portraits=portraits,
            person_tagged_images=tagged_images,
            person_movie_credits=movie_credits,
        )
