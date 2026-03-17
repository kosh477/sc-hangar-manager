"""Application entrypoint."""

from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.db import init_db
from app.routes import register_routes


def create_app() -> Flask:
    """Create and configure Flask application instance."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)
    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
