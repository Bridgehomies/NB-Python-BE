# app/models/cart.py
from typing import Dict
COLLECTION = "carts"

# a cart document:
# {
#   _id: ObjectId,
#   session_id: str,  # can be a cookie or customer token
#   items: [
#       { product_id: ObjectId, quantity: int, price_at_add: float }
#   ],
#   updated_at: datetime,
# }
