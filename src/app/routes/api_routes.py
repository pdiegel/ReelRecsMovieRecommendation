from flask_login import current_user, login_required
from ...services.login_service import get_session_id
from ...constants.api_constants import API_ACCESS_TOKEN
from flask import jsonify, request
import tmdbsimple as tmdb


def set_up_api_routes(app, account: tmdb.Account):
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

    @app.route("/rate_movie/", methods=["POST"])
    @login_required
    def rate() -> str:
        data = request.get_json()
        movie_id = data.get("movie_id", None)
        rating = data.get("rating", None)

        try:
            tmdb.Movies(movie_id).rating(
                value=rating, session_id=get_session_id()
            )
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
