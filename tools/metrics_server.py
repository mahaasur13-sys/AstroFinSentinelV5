#!/usr/bin/env python3
"""Prometheus metrics server for AstroFin Sentinel V5.

Optional authentication via METRICS_AUTH_ENABLED / METRICS_API_KEY.
"""

import argparse
import os

from aiohttp import web
from prometheus_client import REGISTRY, generate_latest

METRICS_AUTH_ENABLED = os.getenv("METRICS_AUTH_ENABLED", "false").lower() == "true"
METRICS_API_KEY = os.getenv("METRICS_API_KEY", "")


async def metrics_handler(request):
    # Check authentication if enabled
    if METRICS_AUTH_ENABLED:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header.split(" ", 1)[1] != METRICS_API_KEY:
            return web.Response(text="Unauthorized", status=401)
    return web.Response(body=generate_latest(REGISTRY), content_type="text/plain")


async def health_handler(request):
    return web.Response(text="OK", content_type="text/plain")


def run_server(port: int = 9091, host: str = "0.0.0.0"):
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    app.router.add_get("/health", health_handler)
    web.run_app(app, port=port, host=host, print=lambda *_: None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AstroFin Prometheus metrics server")
    parser.add_argument("--port", type=int, default=9091)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    run_server(args.port, args.host)
