# NextJS + FastAPI E-commerce Backend

This backend uses FastAPI and MongoDB Atlas and is designed for a Next.js 15+ frontend. It supports:
- Public products listing
- Wishlist / Cart operations
- Guest checkout with optional profile saving
- Reviews
- Admin product management and sales stats
- Cloudinary-backed image uploads (signed)

## Quick start (dev)

1. Copy `.env.example` → `.env` and fill credentials.
2. Install deps: `pip install -r requirements.txt` or use Poetry.
3. Run: `uvicorn app.main:app --reload --port 8000`

## OpenAPI / SDK
`/openapi.json` is available automatically. Use the included script `scripts/generate_sdk.sh` to produce a TypeScript SDK via OpenAPI Generator.

## Notes
- Database is MongoDB Atlas (async using Motor).
- Cloudinary is used for image hosting.
- Admin endpoints require a JWT token (get via `/admin/login`).
