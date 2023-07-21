from ..app.routes import set_up_routes
from ..app.app_instance import app
import os

FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"


def main():
    set_up_routes(app)
    app.run(debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
