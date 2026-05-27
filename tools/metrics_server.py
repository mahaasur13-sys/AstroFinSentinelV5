#!/usr/bin/env python3
"""Prometheus metrics server for AstroFin Sentinel V5."""

import argparse
from aiohttp import web
from prometheus_client import Counter, Gauge, generate_latest, REGISTRY

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

async def metrics_handler(request):
    return web.Response(body=generate_latest(REGISTRY), content_type='text/plain')

def run_server(port=9091):
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    web.run_app(app, port=port, print=lambda *_: None)  # тихий запуск
    # Примечание: web.run_app блокирует поток, для интеграции в асинхронный оркестратор
    # нужно использовать другой подход — см. следующий срез.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9091)
    args = parser.parse_args()
    run_server(args.port)
