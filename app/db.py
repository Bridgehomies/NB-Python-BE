# app/db.py
from __future__ import annotations # Important for postponed evaluation of type annotations
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

# Globals for lazy initialization
# Using Python 3.10+ union syntax (Type | None) with __future__ annotations
# Adding # type: ignore to suppress persistent Pylance errors
_client: AsyncIOMotorClient | None = None # type: ignore
_db: AsyncIOMotorDatabase | None = None # type: ignore


def get_client() -> AsyncIOMotorClient: # type: ignore
    """
    Returns a singleton instance of AsyncIOMotorClient.
    Initializes the client if it hasn't been already.
    """
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI, uuidRepresentation="standard")
    return _client


def get_db() -> AsyncIOMotorDatabase: # type: ignore
    """
    Returns a singleton instance of AsyncIOMotorDatabase.
    Initializes the database connection if it hasn't been already.
    """
    global _db
    if _db is None:
        client = get_client()
        _db = client[settings.MONGO_DB]
    return _db


async def close_client():
    """
    Closes the MongoDB client connection if it exists.
    """
    global _client
    if _client:
        _client.close()
        _client = None

