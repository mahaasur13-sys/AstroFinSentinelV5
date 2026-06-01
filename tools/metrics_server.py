#!/usr/bin/env python3
"""Prometheus metrics server — single source of truth for all AstroFin metrics.

Code imports from here (core/, knowledge/, backtest/, etc.) NOT from meta_rl/metrics.
meta_rl/metrics only holds evolution-specific metrics to avoid circular imports.
"""
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
import argparse

REGISTRY = CollectorRegistry()

# ── HTTP requests ────────────────────────────────────────────────────────
REQUEST_COUNT = Counter("astrofin_request_count", "HTTP requests", ["method", "endpoint"], registry=REGISTRY)
REQUEST_LATENCY = Histogram("astrofin_request_latency_seconds", "Request latency", ["method", "endpoint"], buckets=(0.01, 0.05, 0.1, 0.5, 1, 5), registry=REGISTRY)
REQUEST_ERRORS = Counter("astrofin_request_errors", "Failed requests", ["method", "endpoint"], registry=REGISTRY)

# ── Cache ─────────────────────────────────────────────────────────────────
CACHE_HITS = Counter("astrofin_cache_hits_total", "Cache hits", registry=REGISTRY)
CACHE_MISSES = Counter("astrofin_cache_misses_total", "Cache misses", registry=REGISTRY)

# ── Ollama / LLM ──────────────────────────────────────────────────────────
OLLAMA_STATUS = Gauge("astrofin_ollama_status", "Ollama API health (1=up, 0=down)", registry=REGISTRY)
OLLAMA_ERRORS = Counter("astrofin_ollama_errors_total", "Ollama errors", registry=REGISTRY)
OLLAMA_LATENCY = Histogram("astrofin_ollama_latency_seconds", "Ollama API latency", buckets=(0.1, 0.5, 1, 2, 5, 10), registry=REGISTRY)

# ── Broker ─────────────────────────────────────────────────────────────────
BROKER_ERRORS = Counter("astrofin_broker_errors_total", "Message broker errors", registry=REGISTRY)
BROKER_MESSAGES = Counter("astrofin_broker_messages_total", "Messages published", ["topic", "direction"], registry=REGISTRY)
BROKER_PUBLISH_LATENCY = Histogram("astrofin_broker_publish_latency_seconds", "Publish latency", buckets=(0.001, 0.005, 0.01, 0.05, 0.1), registry=REGISTRY)

# ── RAG ────────────────────────────────────────────────────────────────────
RAG_CHUNK_COUNT = Gauge("astrofin_rag_chunk_count", "Indexed RAG chunks", registry=REGISTRY)
RAG_QUERY_CACHE_HITS = Counter("astrofin_rag_query_cache_hits_total", "RAG query cache hits", registry=REGISTRY)
RAG_QUERY_CACHE_MISSES = Counter("astrofin_rag_query_cache_misses_total", "RAG query cache misses", registry=REGISTRY)
RAG_RELEVANCE_SCORE = Gauge("astrofin_rag_relevance_score", "Average RAG relevance score", registry=REGISTRY)

# ── Backtest ────────────────────────────────────────────────────────────────
BACKTEST_REAL_RUNS = Counter("astrofin_backtest_runs_total", "Real backtest runs", registry=REGISTRY)
BACKTEST_DURATION = Histogram("astrofin_backtest_duration_seconds", "Backtest wall-clock duration", buckets=(1, 5, 10, 30, 60, 300, 600), registry=REGISTRY)
BACKTEST_SYNTHETIC_RUNS = Counter("astrofin_backtest_synthetic_runs_total", "Synthetic backtest runs", registry=REGISTRY)
BACKTEST_SYNTHETIC_DURATION = Histogram("astrofin_backtest_synthetic_duration_seconds", "Synthetic backtest duration", buckets=(0.5, 1, 5, 10, 30, 60), registry=REGISTRY)

# ── Agents ──────────────────────────────────────────────────────────────────
AGENT_EXECUTION_COUNT = Counter("astrofin_agent_execution_count_total", "Agent executions", ["agent_name"], registry=REGISTRY)
AGENT_EXECUTION_DURATION = Histogram("astrofin_agent_execution_duration_seconds", "Agent execution time", ["agent_name"], buckets=(0.1, 0.5, 1, 5, 10, 30, 60), registry=REGISTRY)
AGENT_SELECTION_COUNTS = Counter("astrofin_agent_selection_counts", "Agent selection count", ["agent_name", "pool"], registry=REGISTRY)
AGENT_DURATION = Histogram("astrofin_agent_duration_seconds", "Agent async duration", ["agent_name"], buckets=(0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30), registry=REGISTRY)

# ── Thompson sampling ────────────────────────────────────────────────────────
THOMPSON_PARAMS = Gauge("astrofin_thompson_params", "Thompson sampling params", ["agent_name", "param"], registry=REGISTRY)

# ── Evolution (imported from meta_rl.metrics, non-circular) ─────────────────
try:
    from meta_rl.metrics import (
        EVOLUTION_RUNS, EVOLUTION_COMPLETED, EVOLUTION_ABORTED,
        GENERATION_CURRENT, BEST_REWARD, MEAN_REWARD, REWARD_STD, POPULATION_SIZE, TOP_STRATEGY_ID,
        GENERATIONS_TOTAL, STRATEGIES_CREATED, STRATEGIES_EVALUATED,
        EVOLUTION_DURATION, GENERATION_DURATION, SIGNALS_TOTAL,
    )
except ImportError:
    EVOLUTION_RUNS = Counter("astrofin_evolution_runs_total", "Evolution runs started", registry=REGISTRY)
    EVOLUTION_COMPLETED = Counter("astrofin_evolution_completed_total", "Evolution runs completed", registry=REGISTRY)
    EVOLUTION_ABORTED = Counter("astrofin_evolution_aborted_total", "Evolution runs aborted", registry=REGISTRY)
    GENERATION_CURRENT = Gauge("astrofin_evolution_generation_current", "Current generation", registry=REGISTRY)
    BEST_REWARD = Gauge("astrofin_evolution_best_reward", "Best reward", registry=REGISTRY)
    MEAN_REWARD = Gauge("astrofin_evolution_mean_reward", "Mean reward", registry=REGISTRY)
    REWARD_STD = Gauge("astrofin_evolution_reward_std", "Reward std", registry=REGISTRY)
    POPULATION_SIZE = Gauge("astrofin_evolution_population_size", "Population size", registry=REGISTRY)
    TOP_STRATEGY_ID = Gauge("astrofin_evolution_top_strategy_id", "Top strategy ID", registry=REGISTRY)
    GENERATIONS_TOTAL = Counter("astrofin_evolution_generations_total", "Total generations", registry=REGISTRY)
    STRATEGIES_CREATED = Counter("astrofin_evolution_strategies_created_total", "Strategies created", registry=REGISTRY)
    STRATEGIES_EVALUATED = Counter("astrofin_evolution_strategies_evaluated_total", "Strategies evaluated", registry=REGISTRY)
    EVOLUTION_DURATION = Histogram("astrofin_evolution_duration_seconds", "Evolution duration", buckets=(30, 60, 120, 300, 600, 1800, 3600), registry=REGISTRY)
    GENERATION_DURATION = Histogram("astrofin_evolution_generation_duration_seconds", "Generation duration", buckets=[1, 5, 10, 30, 60, 120, 300], registry=REGISTRY)
    SIGNALS_TOTAL = Counter("astrofin_evolution_signals_total", "Signals", ["signal"], registry=REGISTRY)


def run_server(port: int = 9091, host: str = "0.0.0.0"):
    from aiohttp import web
    async def metrics_handler(request):
        return web.Response(body=generate_latest(REGISTRY), content_type="text/plain")
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    web.run_app(app, port=port, host=host, print=lambda *_: None)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="AstroFin Prometheus metrics server")
    p.add_argument("--port", type=int, default=9091)
    p.add_argument("--host", default="0.0.0.0")
    run_server(p.parse_args().port, p.parse_args().host)