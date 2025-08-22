# app/utils/pagination.py
from typing import Tuple

DEFAULT_LIMIT = 24
MAX_LIMIT = 200


def parse_limit_offset(limit: int | None, offset: int | None) -> Tuple[int, int]:
    if not limit:
        limit = DEFAULT_LIMIT
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT
    if not offset or offset < 0:
        offset = 0
    return int(limit), int(offset)
