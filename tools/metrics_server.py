#!/usr/bin/env python3
"""Prometheus metrics server for AstroFin Sentinel V5.

Re-exports metrics from meta_rl.metrics so that code importing from
tools.metrics_server continues to work (backward compatibility), while
the actual metric definitions live in meta_rl.metrics as the single source of truth.
"""
import argparse
from aiohttp import web
from prometheus_client import REGISTRY, generate_latest

# Re-export everything from meta_rl.metrics for backward compatibility
from meta_rl.metrics import (
    # Evolution
    EVOLUTION_RUNS, EVOLUTION_COMPLETED, EVOLUTION_ABORTED,
    GENERATION_CURRENT, BEST_REWARD, MEAN_REWARD, REWARD_STD, POPULATION_SIZE, TOP_STRATEGY_ID,
    GENERATIONS_TOTAL, STRATEGIES_CREATED, STRATEGIES_EVALUATED,
    EVOLUTION_DURATION, GENERATION_DURATION, SIGNALS_TOTAL,
    # App
    REQUEST_COUNT, REQUEST_LATENCY, REQUEST_ERRORS,
    CACHE_HITS, CACHE_MISSES,
    OLLAMA_STATUS, OLLAMA_ERRORS, OLLAMA_LATENCY,
    BROKER_ERRORS, BROKER_MESSAGES, BROKER_PUBLISH_LATENCY,
    RAG_CHUNK_COUNT, RAG_QUERY_CACHE_HITS, RAG_QUERY_CACHE_MISSES, RAG_RELEVANCE_SCORE,
    BACKTEST_RUNS, BACKTEST_DURATION, BACKTEST_SYNTHETIC_RUNS, BACKTEST_SYNTHETIC_DURATION,
    AGENT_EXECUTION_COUNT, AGENT_EXECUTION_DURATION, AGENT_SELECTION_COUNTS, THOMPSON_PARAMS,
)


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