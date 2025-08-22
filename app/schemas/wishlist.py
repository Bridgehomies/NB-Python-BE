# app/schemas/wishlist.py
from pydantic import BaseModel
from typing import List


class WishlistAdd(BaseModel):
    owner: str
    product_id: str


class WishlistResponse(BaseModel):
    owner: str
    items: List[str]
