"""JWT helper utilities."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)


DEFAULT_ACCESS_EXPIRES = timedelta(minutes=30)
DEFAULT_REFRESH_EXPIRES = timedelta(days=7)


def generate_tokens(identity: str) -> Dict[str, Any]:
    """Generate access and refresh tokens for the given identity."""
    access_token = create_access_token(identity=identity, expires_delta=DEFAULT_ACCESS_EXPIRES)
    refresh_token = create_refresh_token(identity=identity, expires_delta=DEFAULT_REFRESH_EXPIRES)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }