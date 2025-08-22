# backend/app/models/order.py

from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING

# just a string, not a db object
COLLECTION = "orders"

async def ensure_order_indexes(db):
    await db[COLLECTION].create_index([("user_id", ASCENDING)])
    await db[COLLECTION].create_index([("created_at", ASCENDING)])

def doc_to_out(doc: dict) -> dict:
    """
    Convert MongoDB document to an API-friendly dict.
    """
    return {
        "id": str(doc["_id"]),
        "customer_name": doc.get("customer_name"),
        "items": doc.get("items", []),
        "total_price": doc.get("total_price"),
        "status": doc.get("status", "pending"),
        "created_at": doc.get("created_at", datetime.utcnow()),
    }
