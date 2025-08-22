# app/routers/uploads.py
from fastapi import APIRouter, Depends
from ..utils.cloudinary import cloudinary_signature
from ..deps import get_database

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/cloudinary-sign")
async def get_cloudinary_sign():
    """
    Returns a signed payload for the client to upload images directly to Cloudinary.
    Client should POST to https://api.cloudinary.com/v1_1/<cloud_name>/image/upload
    with fields: file, api_key, timestamp, signature, ...
    """
    sig = cloudinary_signature({})
    return sig
