# app/schemas/stats.py
from pydantic import BaseModel
from typing import List, Dict


class ProductSales(BaseModel):
    product_id: str
    title: str
    qty_sold: int
    revenue: float


class SalesStats(BaseModel):
    total_orders: int
    total_revenue: float
    best_selling: List[ProductSales]
