# app/routers/checkout.py
from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_database, get_optional_customer_token
from ..schemas.order import CheckoutRequest, OrderResponse
from ..models.order import COLLECTION as ORDERS_COLL, ensure_order_indexes
from ..models.product import COLLECTION as PRODUCT_COLL
from ..models.customer import COLLECTION as CUSTOMERS_COLL, generate_customer_token
from bson import ObjectId
import datetime
import secrets

router = APIRouter(prefix="/checkout", tags=["checkout"])


async def _gen_order_number(db, prefix="ORD"):
    # Basic order number generator: prefix + unix timestamp + random
    return f"{prefix}-{int(datetime.datetime.utcnow().timestamp())}-{secrets.token_hex(3)}"


@router.post("/", response_model=OrderResponse)
async def checkout(payload: CheckoutRequest, db=Depends(get_database), customer_token=Depends(get_optional_customer_token)):
    # Validate items and compute totals
    subtotal = 0.0
    items_out = []
    for it in payload.items:
        pid = it.get("product_id")
        qty = int(it.get("quantity", 1))
        if not ObjectId.is_valid(pid):
            raise HTTPException(status_code=400, detail=f"Invalid product id: {pid}")
        prod = await db[PRODUCT_COLL].find_one({"_id": ObjectId(pid)})
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        price = prod.get("sale_price") if prod.get("on_sale") and prod.get("sale_price") else prod.get("price")
        items_out.append({"product_id": ObjectId(pid), "title": prod.get("title"), "qty": qty, "price": float(price)})
        subtotal += float(price) * qty

    # Simple totals (no taxes/shipping calculation here — extend as needed)
    total = subtotal

    order_number = await _gen_order_number(db)
    now = datetime.datetime.utcnow()

    order_doc = {
        "order_number": order_number,
        "items": items_out,
        "subtotal": subtotal,
        "total": total,
        "customer": payload.customer.dict(),
        "status": "pending",
        "created_at": now,
    }

    await db[ORDERS_COLL].insert_one(order_doc)

    # optional save profile
    saved_token = None
    if payload.save_profile:
        token = generate_customer_token()
        cust = {
            "token": token,
            "name": payload.customer.name,
            "email": payload.customer.email,
            "phone": payload.customer.phone,
            "address": payload.customer.address,
            "created_at": now,
        }
        await db[CUSTOMERS_COLL].update_one({"email": cust["email"]}, {"$set": cust}, upsert=True)
        saved_token = token

    # Decrement product stock (best-effort, not transactional)
    for it in items_out:
        await db[PRODUCT_COLL].update_one({"_id": it["product_id"], "stock": {"$gte": it["qty"]}}, {"$inc": {"stock": -it["qty"]}})

    # return
    response = {
        "order_number": order_number,
        "status": "pending",
        "total": total,
        "created_at": now.isoformat(),
    }
    if saved_token:
        # include saved token in header or body as convenience
        response["customer_token"] = saved_token

    return response
