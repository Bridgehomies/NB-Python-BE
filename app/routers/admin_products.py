# app/routers/admin_products.py
from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_database, get_admin_user
from ..schemas.product import ProductCreate, ProductUpdate
from ..models.product import COLLECTION as PRODUCT_COLL, doc_to_out
from bson import ObjectId
import datetime

router = APIRouter(prefix="/admin/products", tags=["admin_products"])


@router.post("/", dependencies=[Depends(get_admin_user)])
async def create_product(payload: ProductCreate, db=Depends(get_database)):
    now = datetime.datetime.utcnow()
    doc = {
        "title": payload.title,
        "description": payload.description,
        "price": payload.price,
        "sale_price": None,
        "on_sale": False,
        "images": payload.images or [],
        "stock": payload.stock,
        "metadata": payload.metadata or {},
        "created_at": now,
        "updated_at": now,
    }
    res = await db[PRODUCT_COLL].insert_one(doc)
    return {"id": str(res.inserted_id)}


@router.patch("/{product_id}", dependencies=[Depends(get_admin_user)])
async def update_product(product_id: str, payload: ProductUpdate, db=Depends(get_database)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    update = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if "on_sale" in update and update.get("on_sale") is False:
        update["sale_price"] = None
    update["updated_at"] = datetime.datetime.utcnow()
    await db[PRODUCT_COLL].update_one({"_id": ObjectId(product_id)}, {"$set": update})
    doc = await db[PRODUCT_COLL].find_one({"_id": ObjectId(product_id)})
    return doc_to_out(doc)


@router.delete("/{product_id}", dependencies=[Depends(get_admin_user)])
async def delete_product(product_id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    await db[PRODUCT_COLL].delete_one({"_id": ObjectId(product_id)})
    return {"ok": True}
