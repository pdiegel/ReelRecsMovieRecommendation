import os

from ..app.app_instance import app, login_manager
from ..app.routes import set_up_routes


def main():
    set_up_routes(app, login_manager)
    app.run(debug=is_flask_debug_enabled())


def is_flask_debug_enabled():
    return os.environ.get("FLASK_DEBUG", "False").lower() == "true"


if __name__ == "__main__":
    main()
