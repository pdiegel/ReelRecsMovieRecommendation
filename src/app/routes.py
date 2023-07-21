from ..app.utils import render_movies
from ..constants.api_constants import (
    POPULAR_MOVIES_URL,
    COOKING_MOVIES_URL,
    GENRE_SEARCH_URL,
)


def set_up_routes(app):
    @app.route("/")
    def home():
        return render_movies(POPULAR_MOVIES_URL)

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
