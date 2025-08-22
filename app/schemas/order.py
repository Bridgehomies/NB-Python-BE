# backend/app/schemas/order.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict


class CheckoutItem(BaseModel):
    product_id: str
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]
    email: Optional[EmailStr] = None
    shipping_address: Optional[Dict] = None
    billing_address: Optional[Dict] = None
    payment_method: Optional[str] = "cod"  # cash on delivery / stripe / etc.


class OrderResponse(BaseModel):
    id: str
    status: str
    total_amount: float
    items: List[Dict]

class OrderOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None
    status: str
    total_amount: float
    items: List[Dict]
    created_at: Optional[str] = None
