#!/usr/bin/env python3
"""Prometheus metrics server for AstroFin Sentinel V5.

All metric definitions live in meta_rl.metrics — this server just exposes them
at /metrics via the default prometheus_client REGISTRY.
"""
import argparse

from aiohttp import web
from prometheus_client import REGISTRY, generate_latest


async def metrics_handler(request):
    return web.Response(body=generate_latest(REGISTRY), content_type="text/plain")


def run_server(port: int = 9091, host: str = "0.0.0.0"):
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    web.run_app(app, port=port, host=host, print=lambda *_: None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AstroFin Prometheus metrics server")
    parser.add_argument("--port", type=int, default=9091)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    run_server(args.port, args.host)