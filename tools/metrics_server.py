#!/usr/bin/env python3
"""Prometheus metrics server for AstroFin Sentinel V5."""

import argparse
from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY

# Метрики с префиксом astrofin_
REQUEST_COUNT = Counter('astrofin_requests_total', 'Total orchestration requests')
BROKER_ERRORS = Counter('astrofin_broker_errors_total', 'Broker API errors')
OLLAMA_STATUS = Gauge('astrofin_ollama_available', 'Ollama health check (1=up, 0=down)')
CACHE_HITS = Counter('astrofin_cache_hits_total', 'Cache hit count')
CACHE_MISSES = Counter('astrofin_cache_misses_total', 'Cache miss count')
BACKTEST_REAL_RUNS = Counter('astrofin_backtest_real_runs_total', 'Backtest runs with use_real_agents=True')
BACKTEST_SYNTHETIC_RUNS = Counter('astrofin_backtest_synthetic_runs_total', 'Backtest runs with use_real_agents=False')
AGENT_SELECTION_COUNTS = Counter(
    'astrofin_agent_selection_total',
    'How many times each agent was selected by Thompson Sampling',
    ['agent_name', 'pool']
)
AGENT_SIGNAL_DISTRIBUTION = Counter(
    'astrofin_agent_signal_total',
    'Count of signals (LONG/SHORT/NEUTRAL) per agent',
    ['agent_name', 'signal']
)
THOMPSON_PARAMS = Gauge(
    'astrofin_thompson_params',
    'Thompson Beta parameters per agent',
    ['agent_name', 'param']
)
RAG_RELEVANCE_SCORE = Gauge('astrofin_rag_relevance_avg', 'Average relevance score of last RAG query')
RAG_CHUNK_COUNT = Gauge('astrofin_rag_chunk_count', 'Number of chunks returned in the last RAG query')
RAG_QUERY_CACHE_HITS = Counter('astrofin_rag_query_cache_hits_total', 'Number of RAG query cache hits')
RAG_QUERY_CACHE_MISSES = Counter('astrofin_rag_query_cache_misses_total', 'Number of RAG query cache misses')

# Новая метрика: длительность выполнения агента
AGENT_DURATION = Histogram(
    'astrofin_agent_duration_seconds',
    'Duration of agent execution',
    ['agent_name']
)

async def metrics_handler(request):
    return web.Response(body=generate_latest(REGISTRY), content_type='text/plain')

def run_server(port=9091, host="0.0.0.0"):
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    web.run_app(app, port=port, host=host, print=lambda *_: None)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9091)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    run_server(args.port, args.host)
