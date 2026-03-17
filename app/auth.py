"""Authentication helpers for password hashing and JWT auth."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import current_app, g, request


class AuthError(Exception):
    """Authentication/authorization failure."""

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def hash_password(password: str) -> str:
    """Return bcrypt hash for plaintext password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Compare plaintext password with bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    """Create signed JWT access token."""
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=current_app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"])
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise AuthError("Invalid token type")
    return payload


def _extract_bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    parts = header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise AuthError("Authorization Bearer token is required")
    return parts[1].strip()


def require_auth(func):
    """Ensure request has valid Bearer token and expose current user id in `g.current_user_id`."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = _extract_bearer_token()
        payload = decode_access_token(token)
        try:
            g.current_user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthError("Invalid token payload") from exc
        return func(*args, **kwargs)

    return wrapper


def require_same_user(user_id: int):
    """Ensure authenticated user accesses own resources only."""
    if getattr(g, "current_user_id", None) != user_id:
        raise AuthError("Access denied", status_code=403)
