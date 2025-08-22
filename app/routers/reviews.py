# app/routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..deps import get_database
from ..schemas.review import ReviewCreate, ReviewOut
from ..models.review import COLLECTION as REVIEWS_COLL
from ..models.product import COLLECTION as PRODUCT_COLL
from bson import ObjectId
import datetime

router = APIRouter(prefix="/reviews", tags=["reviews"])

def review_doc_to_out(doc) -> dict:
    """Convert MongoDB document to API response format"""
    return {
        "id": str(doc["_id"]),
        "product_id": str(doc.get("product_id")),
        "author": doc.get("author", "Anonymous"),
        "rating": doc.get("rating", 0),
        "comment": doc.get("comment", ""),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
    }

@router.get("/", response_model=List[dict])
async def list_all_reviews(db=Depends(get_database)):
    """
    Return all reviews (best limited on frontend for dashboard use).
    """
    cursor = db[REVIEWS_COLL].find().sort("created_at", -1)
    out = []
    async for d in cursor:
        out.append(review_doc_to_out(d))
    return out

@router.post("/", status_code=201)
async def create_review(payload: ReviewCreate, db=Depends(get_database)):
    """
    Create a new review for a product.
    """
    # Validate product ID format
    if not ObjectId.is_valid(payload.product_id):
        raise HTTPException(status_code=400, detail="Invalid product id format")
    
    # Check if product exists
    prod = await db[PRODUCT_COLL].find_one({"_id": ObjectId(payload.product_id)})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate rating range
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create review document
    now = datetime.datetime.utcnow()
    review_doc = {
        "product_id": ObjectId(payload.product_id),
        "author": payload.author or "Anonymous",
        "rating": payload.rating,
        "comment": payload.comment or "",
        "created_at": now,
    }
    
    # Insert review
    result = await db[REVIEWS_COLL].insert_one(review_doc)
    
    # Update product rating and review count
    await update_product_rating(db, payload.product_id)
    
    return {
        "ok": True, 
        "review_id": str(result.inserted_id),
        "message": "Review created successfully"
    }

async def update_product_rating(db, product_id: str):
    """
    Update product's average rating and review count based on all reviews.
    """
    try:
        # Get all reviews for this product
        reviews_cursor = db[REVIEWS_COLL].find({"product_id": ObjectId(product_id)})
        reviews = await reviews_cursor.to_list(length=None)
        
        if reviews:
            # Calculate average rating
            total_rating = sum(review["rating"] for review in reviews)
            avg_rating = total_rating / len(reviews)
            review_count = len(reviews)
        else:
            avg_rating = 0
            review_count = 0
        
        # Update product metadata
        await db[PRODUCT_COLL].update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {
                    "metadata.rating": round(avg_rating, 1),
                    "metadata.reviews": review_count,
                    "updated_at": datetime.datetime.utcnow()
                }
            }
        )
    except Exception as e:
        print(f"Error updating product rating: {e}")

@router.get("/product/{product_id}", response_model=List[dict])
async def list_reviews_for_product(product_id: str, db=Depends(get_database)):
    """
    Get all reviews for a specific product.
    """
    # Validate product ID format
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id format")
    
    # Get reviews for the product
    cursor = db[REVIEWS_COLL].find({"product_id": ObjectId(product_id)}).sort("created_at", -1)
    reviews = []
    async for doc in cursor:
        reviews.append(review_doc_to_out(doc))
    
    return reviews

@router.delete("/{review_id}")
async def delete_review(review_id: str, db=Depends(get_database)):
    """
    Delete a review by ID and update product rating.
    """
    # Validate review ID format
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review id format")
    
    # Find the review to get product_id before deletion
    review = await db[REVIEWS_COLL].find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    product_id = str(review["product_id"])
    
    # Delete the review
    result = await db[REVIEWS_COLL].delete_one({"_id": ObjectId(review_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Update product rating after deletion
    await update_product_rating(db, product_id)
    
    return {"message": f"Review with ID {review_id} deleted successfully"}

@router.get("/stats/{product_id}")
async def get_review_stats(product_id: str, db=Depends(get_database)):
    """
    Get review statistics for a product (rating distribution, etc.).
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id format")
    
    # Aggregate review statistics
    pipeline = [
        {"$match": {"product_id": ObjectId(product_id)}},
        {
            "$group": {
                "_id": "$rating",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": -1}}
    ]
    
    cursor = db[REVIEWS_COLL].aggregate(pipeline)
    rating_distribution = {}
    total_reviews = 0
    total_rating = 0
    
    async for doc in cursor:
        rating = doc["_id"]
        count = doc["count"]
        rating_distribution[rating] = count
        total_reviews += count
        total_rating += rating * count
    
    # Fill in missing ratings with 0
    for i in range(1, 6):
        if i not in rating_distribution:
            rating_distribution[i] = 0
    
    avg_rating = round(total_rating / total_reviews, 1) if total_reviews > 0 else 0
    
    return {
        "total_reviews": total_reviews,
        "average_rating": avg_rating,
        "rating_distribution": rating_distribution
    }