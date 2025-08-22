# app/utils/etag.py
import hashlib
import json
from typing import Any

def compute_etag(obj: Any) -> str:
    """
    Compute a deterministic ETag string for a JSON-serializable object.
    """
    # Ensure canonical representation by sorting keys
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    h = hashlib.sha1(encoded.encode("utf-8")).hexdigest()
    return f'W/"{h}"'
