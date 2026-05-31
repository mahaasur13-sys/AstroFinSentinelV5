"""Rate limiting configuration."""

import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://",  # всегда in‑memory, заголовки работают
    headers_enabled=True,
)
