"""Password hashing utilities."""

from __future__ import annotations

from typing import Tuple

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password."""
    return generate_password_hash(plain_password)


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Verify a candidate password against the stored hash."""
    return check_password_hash(stored_hash, candidate_password)