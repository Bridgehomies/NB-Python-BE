# app/models/review.py
COLLECTION = "reviews"

async def ensure_review_indexes(db):
    """
    Create indexes for the reviews collection to optimize queries.
    """
    # Index on product_id for fast lookups of reviews by product
    await db[COLLECTION].create_index("product_id")
    
    # Index on created_at for sorting reviews by date
    await db[COLLECTION].create_index("created_at")
    
    # Compound index for product_id + created_at for efficient product review queries
    await db[COLLECTION].create_index([("product_id", 1), ("created_at", -1)])
    
    # Index on rating for statistics queries
    await db[COLLECTION].create_index("rating")

# Review document structure:
# {
#   _id: ObjectId,
#   product_id: ObjectId,  # Reference to products collection
#   author: str,           # Name of the reviewer
#   rating: int,           # Rating from 1 to 5
#   comment: str,          # Review text
#   created_at: datetime   # When the review was created
# }