"""Blueprint registration."""

from app.routes.health import health_bp


def register_routes(app):
    """Register all API routes."""
    app.register_blueprint(health_bp)
