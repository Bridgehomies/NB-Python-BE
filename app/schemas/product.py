# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ProductCreate(BaseModel):
    name: str  # Changed from 'title' to 'name' for consistency
    description: Optional[str] = ""
    price: float
    images: Optional[List[str]] = []
    stock: int = 0
    metadata: Optional[Dict] = {}


class ProductUpdate(BaseModel):
    name: Optional[str]  # Changed from 'title' to 'name'
    description: Optional[str]
    price: Optional[float]
    sale_price: Optional[float]
    on_sale: Optional[bool]
    images: Optional[List[str]]
    stock: Optional[int]
    metadata: Optional[Dict]


class ProductOut(BaseModel):
    id: str
    name: str = Field(alias="title", default="Untitled Product")  # Support both 'name' and 'title'
    description: str = ""
    price: float
    sale_price: Optional[float] = None
    on_sale: bool = False
    images: List[str] = []
    stock: int
    inStock: bool = True  # Add this field that frontend expects
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict] = {}

    class Config:
        allow_population_by_field_name = True  # Allow both 'name' and 'title'