"""JWT token creation and validation."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

# Configuration (should come from environment in production)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int, role: str) -> str:
    """Create an access token.

    Args:
        user_id: User ID to include in token.
        role: User role.

    Returns:
        Encoded JWT access token.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create a refresh token.

    Args:
        user_id: User ID to include in token.

    Returns:
        Encoded JWT refresh token.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token.

    Args:
        token: Encoded JWT token.

    Returns:
        Decoded payload dict or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from a token.

    Args:
        token: Encoded JWT token.

    Returns:
        User ID if token is valid, None otherwise.
    """
    payload = decode_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None


def get_role_from_token(token: str) -> Optional[str]:
    """Extract role from a token.

    Args:
        token: Encoded JWT token.

    Returns:
        Role string if token is valid and contains role, None otherwise.
    """
    payload = decode_token(token)
    if payload and "role" in payload:
        return payload["role"]
    return None
