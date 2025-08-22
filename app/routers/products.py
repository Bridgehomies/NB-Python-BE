# backend/app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
from ..deps import get_database
from ..utils.pagination import parse_limit_offset
from ..models.product import COLLECTION as PRODUCT_COLL, doc_to_out
from ..schemas.product import ProductOut
from bson import ObjectId
import json
import datetime
from cloudinary import uploader

router = APIRouter(prefix="/products", tags=["products"])

# --------------------------------------
# GET /products/ (list with filters)
# --------------------------------------
@router.get("/", response_model=List[ProductOut])
async def list_products(
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    subcategories: Optional[List[str]] = Query(None),
    db=Depends(get_database),
):
    """
    Lists products with optional filtering by category and subcategories.
    """
    limit, offset = parse_limit_offset(limit, offset)
    query = {}
    
    if category:
        query["metadata.category"] = {"$regex": f"^{category}$", "$options": "i"}


    if subcategories:
        # Use $in operator to match any of the provided subcategories
        query["metadata.subcategories"] = {"$in": subcategories}

    cursor = (
        db[PRODUCT_COLL]
        .find(query, skip=offset, limit=limit)
        .sort("created_at", -1)
    )
    items = []
    async for d in cursor:
        items.append(doc_to_out(d))
    return items

# --------------------------------------
# GET /products/{id}
# --------------------------------------
@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    d = await db[PRODUCT_COLL].find_one({"_id": ObjectId(product_id)})
    if not d:
        raise HTTPException(status_code=404, detail="Product not found")
    return doc_to_out(d)


# --------------------------------------
# GET /products/subcategories
# --------------------------------------
@router.get("/subcategories")
async def get_subcategories(
    categories: List[str] = Query(None, description="Main categories to filter by (e.g., 'Jewelry', 'Kids', 'Coats')"),
):
    """
    Returns available subcategory options for the given categories.
    """
    if not categories:
        return {}
    
    # Static data for subcategories based on the provided requirements
    all_subcategories = {
        "Jewelry": {
            "Categories": ["NECKLACES", "EARRINGS", "BRACELETS", "RINGS"],
            "Collections": ["CRYSTAL COLLECTION", "PEARL COLLECTION", "STATEMENT PIECES", "MINIMALIST"],
            "Materials": ["GOLD PLATED", "SILVER PLATED", "ROSE GOLD", "GEMSTONES"]
        },
        "Kids": {
            "Categories": ["TOPS", "BOTTOMS", "DRESSES", "OUTERWEAR"],
            "Age Groups": ["BABY (0-2 YEARS)", "TODDLER (2-4 YEARS)", "LITTLE KIDS (4-7 YEARS)", "BIG KIDS (8-12 YEARS)"],
            "Collections": ["CASUAL", "FORMAL", "SCHOOL", "SEASONAL"]
        },
        "Coats": {
            "Group": ["Men's", "Women's"],
            "Categories": ["OVERCOATS", "TRENCH COATS", "PUFFER JACKETS", "PARKAS"],
            "Materials": ["WOOL", "LEATHER", "COTTON", "SYNTHETIC"]
        }
    }
    
    # Filter the data based on the requested categories
    result = {cat: all_subcategories[cat] for cat in categories if cat in all_subcategories}
    
    return result

# --------------------------------------
# POST /products/ (create)
# --------------------------------------
@router.post("/", status_code=201)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    inStock: bool = Form(True),
    sale_price: Optional[float] = Form(None),
    isSale: bool = Form(False),
    isNew: bool = Form(True),
    isFeatured: bool = Form(False),
    rating: int = Form(0),
    reviews: int = Form(0),
    images: List[UploadFile] = File(default=[]),
    # Additional form fields for the new subcategories
    subcategories: str = Form("[]"),
    collections: str = Form("[]"),
    materials: str = Form("[]"),
    groups: str = Form("[]"),
    age_groups: str = Form("[]"),
    db=Depends(get_database),
):
    """
    Create a new product by uploading images to Cloudinary and saving all metadata.
    """
    # Parse JSON strings for lists of attributes
    try:
        subcats = json.loads(subcategories)
        collections_list = json.loads(collections)
        materials_list = json.loads(materials)
        groups_list = json.loads(groups)
        age_groups_list = json.loads(age_groups)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format for subcategories.")

    # Get the stock value based on the `inStock` boolean
    stock_value = 100 if inStock else 0
    created_at_date = datetime.datetime.utcnow()

    image_urls = []
    for image in images:
        try:
            upload_result = uploader.upload(image.file, folder="ecommerce-products")
            image_urls.append(upload_result.get("secure_url"))
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            raise HTTPException(status_code=500, detail="Image upload failed.")
    
    # Combine all subcategory lists into a single list for the database
    all_subcategories = subcats + collections_list + materials_list + groups_list + age_groups_list
    
    doc = {
        "name": name,
        "price": price,
        "sale_price": sale_price,
        "description": description,
        "stock": stock_value,
        "inStock": inStock,
        "created_at": created_at_date,
        "updated_at": datetime.datetime.utcnow(),
        "images": image_urls,
        "metadata": {
            "category": category,
            "subcategories": all_subcategories,
            "isSale": isSale,
            "isNew": isNew,
            "isFeatured": isFeatured,
            "rating": rating,
            "reviews": reviews,
        },
    }

    result = await db[PRODUCT_COLL].insert_one(doc)
    return {"ok": True, "product_id": str(result.inserted_id)}

# --------------------------------------
# DELETE /products/{id} (delete)
# --------------------------------------
@router.delete("/{product_id}")
async def delete_product(product_id: str, db=Depends(get_database)):
    """
    Deletes a product by its ID.
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    result = await db[PRODUCT_COLL].delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": f"Product with ID {product_id} deleted successfully"}