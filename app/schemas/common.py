# app/schemas/common.py
from pydantic import BaseModel
from typing import Optional, List, Any


class IDResponse(BaseModel):
    id: str


class Pagination(BaseModel):
    limit: int
    offset: int
    total: Optional[int] = None
