# app/utils/ids.py
from bson import ObjectId
from typing import Any

def to_str_id(o: Any) -> str:
    if isinstance(o, ObjectId):
        return str(o)
    return str(o)


def ensure_objectid(id_str: str) -> ObjectId:
    if ObjectId.is_valid(id_str):
        return ObjectId(id_str)
    raise ValueError("Invalid ObjectId")


def ensure_str_id(id_val: Any) -> str:
    """Return canonical string id for input (ObjectId or str)."""
    try:
        return to_str_id(id_val)
    except Exception:
        return str(id_val)
