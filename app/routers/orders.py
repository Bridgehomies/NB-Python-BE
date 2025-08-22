# backend/app/routers/orders.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from ..deps import get_database
from ..models.order import COLLECTION as ORDER_COLL, doc_to_out
from ..schemas.order import OrderOut

router = APIRouter(tags=["orders"])

# A new Pydantic model to validate the incoming status update
class OrderUpdate(BaseModel):
    status: str

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["pending", "processing", "ready-to-ship", "shipped", "delivered", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

@router.get("/", response_model=List[OrderOut])
async def list_orders(db=Depends(get_database)):
    cursor = db[ORDER_COLL].find().sort("created_at", -1).limit(50)
    orders = []
    async for d in cursor:
        orders.append(doc_to_out(d))
    return orders

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order id")
    doc = await db[ORDER_COLL].find_one({"_id": ObjectId(order_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Order not found")
    return doc_to_out(doc)

# New route to update an order's status
@router.put("/{order_id}/status", response_model=OrderOut)
async def update_order_status(order_id: str, update: OrderUpdate, db=Depends(get_database)):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order id")

    # Use MongoDB's update_one with the $set operator to update only the status field
    result = await db[ORDER_COLL].update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": update.status}}
    )

    if result.modified_count == 0:
        # If the order wasn't found or the status was already the same
        doc = await db[ORDER_COLL].find_one({"_id": ObjectId(order_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Order not found")
        # If the document was found but not modified, it's not an error.
        # We can just return the existing document.
        return doc_to_out(doc)
    
    # Fetch the updated document to return it in the response
    updated_doc = await db[ORDER_COLL].find_one({"_id": ObjectId(order_id)})
    return doc_to_out(updated_doc)