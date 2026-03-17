"""Blueprint registration."""

from app.routes.api import api_bp
from app.routes.health import health_bp
from app.routes.pages import pages_bp


def register_routes(app):
    """Register all API routes."""
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)
