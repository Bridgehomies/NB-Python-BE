# app/schemas/customer.py
from pydantic import BaseModel
from typing import Optional


class CustomerProfile(BaseModel):
    token: str
    name: str
    email: str
    phone: str
    address: str
