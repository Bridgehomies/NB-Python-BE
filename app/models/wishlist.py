# app/models/wishlist.py
COLLECTION = "wishlists"

# wishlist doc:
# {
#   _id,
#   owner: str,  # either admin id or customer token or session cookie id
#   items: [{product_id, added_at}],
#   created_at
# }
