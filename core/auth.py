import secrets

"""API Key authentication."""
import logging
import os
from functools import wraps

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"
API_KEY = os.getenv("API_KEY", "")


def require_api_key(func):
    """Декоратор для Flask: проверяет X-API-Key."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request

        if not REQUIRE_AUTH:
            return func(*args, **kwargs)
        key = request.headers.get("X-API-Key")
        if not key or not secrets.compare_digest(key, API_KEY):
            logger.warning("auth.failed endpoint=%s remote=%s", request.path, request.remote_addr)
            return ({"error": "Unauthorized"}, 401)
        logger.debug("auth.success endpoint=%s", request.path)
        return func(*args, **kwargs)

    return wrapper


async def fastapi_require_api_key(request: Request):
    """FastAPI dependency: проверяет X-API-Key."""
    if not REQUIRE_AUTH:
        return
    key = request.headers.get("X-API-Key")
    if not key or not secrets.compare_digest(key, API_KEY):
        logger.warning("auth.failed endpoint=%s remote=%s", request.url.path, request.client.host)
        raise HTTPException(status_code=401, detail="Invalid API key")
    logger.debug("auth.success endpoint=%s", request.url.path)
