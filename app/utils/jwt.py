# utils/jwt.py

from datetime import datetime, timedelta
from typing import Optional, Union

from jose import jwt, JWTError

from app.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    :param data: dict payload to encode
    :param expires_delta: custom timedelta, defaults to settings.JWT_EXPIRE_MINUTES
    :return: encoded JWT token as str
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Union[dict, None]:
    """
    Verify a JWT token and return the decoded payload if valid.
    This function returns None on JWTError.
    :param token: JWT string
    :return: dict payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> dict: # Renamed from get_token_payload
    """
    Decode a JWT token and return the decoded payload.
    This function raises JWTError if the token is invalid or expired.
    :param token: JWT string
    :return: dict payload
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

