# app/schemas/review.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    product_id: str
    author: Optional[str] = "Anonymous"
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = ""

class ReviewOut(BaseModel):
    id: str
    product_id: str
    author: str
    rating: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True