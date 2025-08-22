# app/routers/wishlist.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..deps import get_database
from ..models.wishlist import COLLECTION as WISHLIST_COLL
from ..models.product import doc_to_out, COLLECTION as PRODUCT_COLL
from bson import ObjectId
from ..schemas.wishlist import WishlistAdd, WishlistResponse
import datetime

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.post("/add", response_model=WishlistResponse)
async def add_to_wishlist(payload: WishlistAdd, db=Depends(get_database)):
    owner = payload.owner
    product_id = payload.product_id
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    product_obj = await db[PRODUCT_COLL].find_one({"_id": ObjectId(product_id)})
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    # upsert wishlist
    now = datetime.datetime.utcnow()
    await db[WISHLIST_COLL].update_one(
        {"owner": owner},
        {"$addToSet": {"items": {"product_id": ObjectId(product_id), "added_at": now}}, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )
    # return simplified response
    doc = await db[WISHLIST_COLL].find_one({"owner": owner})
    items = [str(it["product_id"]) for it in doc.get("items", [])]
    return {"owner": owner, "items": items}


@router.post("/remove", response_model=WishlistResponse)
async def remove_from_wishlist(payload: WishlistAdd, db=Depends(get_database)):
    owner = payload.owner
    product_id = payload.product_id
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    await db[WISHLIST_COLL].update_one({"owner": owner}, {"$pull": {"items": {"product_id": ObjectId(product_id)}}})
    doc = await db[WISHLIST_COLL].find_one({"owner": owner})
    if not doc:
        return {"owner": owner, "items": []}
    items = [str(it["product_id"]) for it in doc.get("items", [])]
    return {"owner": owner, "items": items}


@router.get("/{owner}", response_model=WishlistResponse)
async def get_wishlist(owner: str, db=Depends(get_database)):
    doc = await db[WISHLIST_COLL].find_one({"owner": owner})
    if not doc:
        return {"owner": owner, "items": []}
    items = [str(it["product_id"]) for it in doc.get("items", [])]
    return {"owner": owner, "items": items}
