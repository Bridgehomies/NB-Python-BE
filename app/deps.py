# app/deps.py
from __future__ import annotations
from fastapi import Depends, HTTPException, status, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from .db import get_db
from .config import settings
from .security import verify_token
from .utils.ids import ensure_str_id

async def get_database() -> AsyncIOMotorDatabase: # type: ignore
    """
    Dependency function to provide a database client.
    """
    return get_db()


async def get_admin_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Admin dependency — expects header: Authorization: Bearer <token>
    Returns admin email string when valid; raises 401 otherwise.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = parts[1]
    sub = verify_token(token)
    if not sub or sub != settings.ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or not admin")
    return sub


async def get_optional_customer_token(x_customer_token: Optional[str] = Header(None)):
    """
    A token header `X-Customer-Token` can identify a saved guest profile.
    """
    if not x_customer_token:
        return None
    return ensure_str_id(x_customer_token)

