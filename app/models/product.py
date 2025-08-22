# app/models/product.py
from typing import Optional, List, Dict
from bson import ObjectId

COLLECTION = "products"

async def ensure_product_indexes(db):
    await db[COLLECTION].create_index("title")
    await db[COLLECTION].create_index("on_sale")
    await db[COLLECTION].create_index([("metadata.category", 1)])

def doc_to_out(d: Dict) -> Dict:
    """
    Converts a MongoDB document to an API-friendly dict.
    
    This function maps the database keys to the keys expected by the
    frontend to correctly display product information.
    
    It assumes that all details except the image URLs are stored directly
    in the MongoDB document.
    """
    out = {
        # The '_id' field from the document is mapped to the 'id' field in the API response.
        "id": str(d.get("_id")),
        # The 'name' field is mapped to 'title' to align with frontend components.
        "title": d.get("name"), 
        "description": d.get("description"),
        "price": d.get("price"),
        "sale_price": d.get("sale_price"),
        "on_sale": bool(d.get("on_sale", False)),
        # The 'images' field is an array of URLs from Cloudinary.
        "images": d.get("images", []),
        "stock": d.get("stock", 0),
        # 'inStock' is derived from the 'stock' field.
        "inStock": d.get("stock", 0) > 0,
        "metadata": d.get("metadata", {}),
        # The 'category' is retrieved from the metadata.
        "category": d.get("metadata", {}).get("category"),
        # 'subcategories' is also retrieved from the metadata.
        "subcategories": d.get("metadata", {}).get("subcategories", []),
        "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
        "updated_at": d.get("updated_at").isoformat() if d.get("updated_at") else None,
    }
    return out
