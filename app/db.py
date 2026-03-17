"""Database extension setup."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app instance."""
    db.init_app(app)
