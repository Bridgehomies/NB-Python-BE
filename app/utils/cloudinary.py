# app/utils/cloudinary.py
import time
import hashlib
from app.config import settings
from typing import Dict


def cloudinary_signature(params: Dict[str, str]) -> Dict[str, str]:
    """
    Minimal helper to create Cloudinary upload signature.
    Client can post direct to Cloudinary with the returned signature.
    """
    timestamp = str(int(time.time()))
    params_to_sign = {k: v for k, v in params.items() if v is not None and v != ""}
    # Cloudinary expects params sorted by key, like "param1=value1&param2=value2..."
    signed_pairs = "&".join(f"{k}={params_to_sign[k]}" for k in sorted(params_to_sign.keys()))
    to_sign = f"{signed_pairs}&timestamp={timestamp}" if signed_pairs else f"timestamp={timestamp}"
    to_hash = f"{to_sign}{settings.CLOUDINARY_API_SECRET}"
    signature = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()
    return {
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "api_key": settings.CLOUDINARY_API_KEY,
        "timestamp": timestamp,
        "signature": signature,
    }
