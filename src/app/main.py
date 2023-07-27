import os

from ..app.app_instance import app, login_manager
from ..app.routes import set_up_routes
import tmdbsimple as tmdb
import requests
from ..constants.api_constants import API_KEY, API_HEADERS


def main():
    tmdb.API_KEY = API_KEY
    tmdb.REQUESTS_SESSION = requests.Session()
    tmdb.REQUESTS_SESSION.headers.update(API_HEADERS)
    account = tmdb.Account("")
    set_up_routes(app, login_manager, account)
    app.run(debug=is_flask_debug_enabled())


def is_flask_debug_enabled():
    return os.environ.get("FLASK_DEBUG", "False").lower() == "true"


if __name__ == "__main__":
    main()
