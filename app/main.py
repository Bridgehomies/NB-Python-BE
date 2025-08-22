# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import get_client, close_client, get_db
from .routers import (
    wishlist,
    cart,
    checkout,
    reviews,
    admin_products,
    admin_stats,
    uploads,
    products,  
    orders,
)
from .models import ensure_product_indexes, ensure_order_indexes, ensure_review_indexes, ensure_customer_indexes
import uvicorn
from .utils.etag import compute_etag
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Ecommerce Backend", version="0.1.0")

# CORS — adjust in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "nabeerabareera.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers

app.include_router(products.router)  # 👈 mount new /products routes
app.include_router(wishlist.router)
app.include_router(cart.router)
app.include_router(checkout.router)
app.include_router(reviews.router)
app.include_router(admin_products.router)
app.include_router(admin_stats.router, prefix="/stats")
app.include_router(uploads.router)
app.include_router(orders.router)


@app.on_event("startup")
async def startup():
    client = get_client()
    db = client[settings.MONGO_DB]

    await ensure_product_indexes(db)
    await ensure_order_indexes(db)
    await ensure_review_indexes(db)
    await ensure_customer_indexes(db)

    logger.info("Connected to Mongo and ensured indexes.")


@app.on_event("shutdown")
async def shutdown():
    await close_client()


@app.middleware("http")
async def etag_middleware(request: Request, call_next):
    response: Response = await call_next(request)

    if request.method == "GET" and "application/json" in (response.headers.get("content-type") or ""):
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            import json
            payload = json.loads(body or b"{}")
            etag = compute_etag(payload)
            response.headers["ETag"] = etag
        except Exception:
            pass

        # ✅ restore body with async iterator
        async def body_iterator():
            yield body

        response.body_iterator = body_iterator()

    return response

    response: Response = await call_next(request)
    # compute weak etag for GET responses with JSON
    if request.method == "GET" and "application/json" in (response.headers.get("content-type") or ""):
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            import json
            payload = json.loads(body or b"{}")
            etag = compute_etag(payload)
            response.headers["ETag"] = etag
        except Exception:
            pass
        # restore body
        response.body_iterator = iter([body])
    return response


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
