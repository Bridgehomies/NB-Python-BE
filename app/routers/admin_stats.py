from __future__ import annotations
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.utils.jwt import decode_access_token

# --- Reusable Dependency ---
# Create a type alias for the database dependency. This helps with static analysis
# and keeps the code DRY (Don't Repeat Yourself).
DBDep = Annotated[AsyncIOMotorDatabase, Depends(get_db)]

# --- Dependency to enforce admin-only access ---
async def get_current_admin(
    authorization: Annotated[str, Header()],
    db: DBDep,
):
    """
    Extracts Bearer token from Authorization header and validates admin.
    """
    try:
        if not authorization.startswith("Bearer "):
            raise ValueError("Invalid auth header format")
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required.",
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token.",
        )


router = APIRouter(
    tags=["admin-stats"],
    dependencies=[Depends(get_current_admin)],
)

# The dependency is already applied at the router level above.

@router.get("/")
async def get_admin_stats(
    db: DBDep,
):
    """
    Return basic stats for admin dashboard.
    """
    users_count = await db["users"].count_documents({})
    products_count = await db["products"].count_documents({})
    orders_count = await db["orders"].count_documents({})

    return {
        "users": users_count,
        "products": products_count,
        "orders": orders_count,
    }


@router.get("/sales/daily")
async def get_daily_sales(
    db: DBDep,
):
    """
    Returns total sales for the last 7 days (grouped by date).
    Expects `orders` collection to have:
      - `created_at`: datetime
      - `total_amount`: number
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    pipeline = [
        {"$match": {"created_at": {"$gte": seven_days_ago}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"},
                },
                "total_sales": {"$sum": "$total_amount"},
                "orders_count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    results = await db["orders"].aggregate(pipeline).to_list(length=None)

    # Format results nicely
    daily_sales = [
        {
            "date": f"{r['_id']['year']}-{r['_id']['month']:02d}-{r['_id']['day']:02d}",
            "total_sales": r["total_sales"],
            "orders_count": r["orders_count"],
        }
        for r in results
    ]

    return {"last_7_days": daily_sales}
