"""Shared base models."""

from app.db import db


class TimestampMixin:
    """Adds created/updated timestamps to inheriting models."""

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
