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
