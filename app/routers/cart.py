# app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_database
from ..models.cart import COLLECTION as CART_COLL
from ..models.product import COLLECTION as PRODUCT_COLL, doc_to_out
from ..schemas.cart import CartCreate, CartResponse
from bson import ObjectId
import datetime

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/upsert", response_model=CartResponse)
async def upsert_cart(payload: CartCreate, db=Depends(get_database)):
    session_id = payload.session_id
    # Normalize items and validate product ids
    items = []
    subtotal = 0.0
    for it in payload.items:
        pid = it.product_id
        if not ObjectId.is_valid(pid):
            raise HTTPException(status_code=400, detail=f"Invalid product id: {pid}")
        prod = await db[PRODUCT_COLL].find_one({"_id": ObjectId(pid)})
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        price = prod.get("sale_price") if prod.get("on_sale") and prod.get("sale_price") else prod.get("price")
        items.append({"product_id": ObjectId(pid), "quantity": int(it.quantity), "price_at_add": float(price)})
        subtotal += float(price) * int(it.quantity)

    now = datetime.datetime.utcnow()
    await db[CART_COLL].update_one(
        {"session_id": session_id},
        {"$set": {"items": items, "updated_at": now}, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )

    response = {
        "session_id": session_id,
        "items": [{"product_id": str(it["product_id"]), "quantity": it["quantity"], "price_at_add": it["price_at_add"]} for it in items],
        "total_items": sum(it["quantity"] for it in items),
        "subtotal": subtotal,
    }
    return response


@router.get("/{session_id}", response_model=CartResponse)
async def get_cart(session_id: str, db=Depends(get_database)):
    doc = await db[CART_COLL].find_one({"session_id": session_id})
    if not doc:
        return {"session_id": session_id, "items": [], "total_items": 0, "subtotal": 0.0}
    items = [{"product_id": str(it["product_id"]), "quantity": it["quantity"], "price_at_add": it["price_at_add"]} for it in doc.get("items", [])]
    subtotal = sum(it["quantity"] * it["price_at_add"] for it in doc.get("items", []))
    return {"session_id": session_id, "items": items, "total_items": sum(it["quantity"] for it in doc.get("items", [])), "subtotal": subtotal}
