# app/models/customer.py
COLLECTION = "customers"

async def ensure_customer_indexes(db):
    await db[COLLECTION].create_index("name")
    await db[COLLECTION].create_index("category")
    
# customer doc:
# {
#   _id,
#   token: str,  # random token for guest reuse
#   name, email, phone, address,
#   created_at
# }

import secrets

def generate_customer_token() -> str:
    return secrets.token_urlsafe(22)

async def ensure_customer_indexes(db):
    await db[COLLECTION].create_index("token", unique=True)
    await db[COLLECTION].create_index("email")
