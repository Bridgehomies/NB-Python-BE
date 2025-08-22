# app/schemas/cart.py
from pydantic import BaseModel
from typing import List, Dict


class CartItem(BaseModel):
    product_id: str
    quantity: int


class CartCreate(BaseModel):
    session_id: str  # cookie or customer token
    items: List[CartItem]


class CartResponse(BaseModel):
    session_id: str
    items: List[Dict]
    total_items: int
    subtotal: float
