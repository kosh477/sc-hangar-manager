"""Application entrypoint."""

from flask import Flask, jsonify
from dotenv import load_dotenv

from app.auth import AuthError
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

    @app.errorhandler(AuthError)
    def handle_auth_error(err: AuthError):
        return jsonify({"error": err.message}), err.status_code

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
