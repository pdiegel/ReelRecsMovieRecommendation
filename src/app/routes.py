from main import render_movies, app
from constants import POPULAR_MOVIES_URL, COOKING_MOVIES_URL, GENRE_SEARCH_URL


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
