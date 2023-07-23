from ..app.routes import set_up_routes
from ..app.app_instance import app, login_manager
import os

FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"


def main():
    set_up_routes(app, login_manager)
    app.run(debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
