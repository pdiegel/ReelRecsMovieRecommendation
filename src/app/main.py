import os
from .flask_app import app


def main():
    app.run(debug=is_flask_debug_enabled())


def is_flask_debug_enabled():
    return os.environ.get("FLASK_DEBUG", "False").lower() == "true"


if __name__ == "__main__":
    main()
