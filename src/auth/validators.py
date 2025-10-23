"""Input validation helpers for authentication endpoints."""

from __future__ import annotations

import re
from typing import Tuple

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def validate_registration_input(email: str, password: str) -> Tuple[bool, str | None]:
    """Validate registration data."""
    if not email or not EMAIL_REGEX.match(email):
        return False, "Please provide a valid email address."
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return False, "Password must be at least 8 characters long."
    return True, None