"""Prometheus metrics for AstroFin Sentinel V5.

metrics_server.py is the single source of truth. This module re-exports
evolution-specific metrics so that meta_rl/ can import them without circular
imports. Both modules share the same global REGISTRY.
"""
from prometheus_client import Counter, Gauge, Histogram

# ── Evolution lifecycle ────────────────────────────────────────────────
EVOLUTION_RUNS = Counter(
    "astrofin_evolution_runs_total",
    "Total number of evolution runs started",
)
EVOLUTION_COMPLETED = Counter(
    "astrofin_evolution_completed_total",
    "Total number of evolution runs that finished all generations",
)
EVOLUTION_ABORTED = Counter(
    "astrofin_evolution_aborted_total",
    "Total number of evolution runs that aborted",
)

# ── Per-generation (latest values) ──────────────────────────────────────
GENERATION_CURRENT = Gauge(
    "astrofin_evolution_generation_current",
    "Current generation number (0 if idle)",
)
BEST_REWARD = Gauge(
    "astrofin_evolution_best_reward",
    "Best (max) reward in the active evolution run",
)
MEAN_REWARD = Gauge(
    "astrofin_evolution_mean_reward",
    "Mean reward of the last evaluated generation",
)
REWARD_STD = Gauge(
    "astrofin_evolution_reward_std",
    "Std dev of rewards in the last evaluated generation",
)
POPULATION_SIZE = Gauge(
    "astrofin_evolution_population_size",
    "Number of strategies in current population",
)
TOP_STRATEGY_ID = Gauge(
    "astrofin_evolution_top_strategy_id",
    "ID of the current best strategy (label holds the ID; value always 1)",
)

# ── Cumulative counters ───────────────────────────────────────────────
GENERATIONS_TOTAL = Counter(
    "astrofin_evolution_generations_total",
    "Total generations completed across all runs",
)
STRATEGIES_CREATED = Counter(
    "astrofin_evolution_strategies_created_total",
    "Total strategies created",
)
STRATEGIES_EVALUATED = Counter(
    "astrofin_evolution_strategies_evaluated_total",
    "Total individual strategy evaluations",
)

# ── Timing ─────────────────────────────────────────────────────────────
EVOLUTION_DURATION = Histogram(
    "astrofin_evolution_duration_seconds",
    "Duration of complete evolution runs",
    buckets=(30, 60, 120, 300, 600, 1800, 3600),
)
GENERATION_DURATION = Histogram(
    "astrofin_evolution_generation_duration_seconds",
    "Wall-clock duration of each generation",
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

# ── Signals from top strategy ──────────────────────────────────────────
SIGNALS_TOTAL = Counter(
    "astrofin_evolution_signals_total",
    "Signals (LONG/SHORT/NEUTRAL) from the top strategy",
    ["signal"],
)

# ── App-level (agents, cache, broker, RAG, backtest) ───────────────────
REQUEST_COUNT = Counter(
    "astrofin_request_count_total", "Total HTTP requests",
    ["method", "endpoint"],
)
REQUEST_LATENCY = Histogram(
    "astrofin_request_latency_seconds", "Request latency",
    ["method", "endpoint"], buckets=(0.01, 0.05, 0.1, 0.5, 1, 5),
)
REQUEST_ERRORS = Counter(
    "astrofin_request_errors_total", "Failed requests",
    ["method", "endpoint"],
)
CACHE_HITS = Counter("astrofin_cache_hits_total", "Cache hits")
CACHE_MISSES = Counter("astrofin_cache_misses_total", "Cache misses")
OLLAMA_STATUS = Gauge("astrofin_ollama_status", "Ollama API health (1=up, 0=down)")
OLLAMA_ERRORS = Counter("astrofin_ollama_errors_total", "Ollama errors")
OLLAMA_LATENCY = Histogram(
    "astrofin_ollama_latency_seconds", "Ollama API latency",
    buckets=(0.1, 0.5, 1, 2, 5, 10),
)
BROKER_ERRORS = Counter("astrofin_broker_errors_total", "Message broker errors")
BROKER_MESSAGES = Counter(
    "astrofin_broker_messages_total", "Messages published",
    ["topic", "direction"],
)
BROKER_PUBLISH_LATENCY = Histogram(
    "astrofin_broker_publish_latency_seconds", "Publish latency",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1),
)
RAG_CHUNK_COUNT = Gauge("astrofin_rag_chunk_count", "Indexed RAG chunks")
RAG_QUERY_CACHE_HITS = Counter("astrofin_rag_query_cache_hits_total", "RAG query cache hits")
RAG_QUERY_CACHE_MISSES = Counter("astrofin_rag_query_cache_misses_total", "RAG query cache misses")
RAG_RELEVANCE_SCORE = Gauge("astrofin_rag_relevance_score", "Avg RAG retrieval relevance score")
BACKTEST_RUNS = Counter("astrofin_backtest_runs_total", "Backtest runs")
BACKTEST_DURATION = Histogram(
    "astrofin_backtest_duration_seconds", "Backtest duration",
    buckets=(1, 5, 10, 30, 60, 120, 300, 600),
)
BACKTEST_SYNTHETIC_RUNS = Counter("astrofin_backtest_synthetic_runs_total", "Synthetic backtest runs")
BACKTEST_SYNTHETIC_DURATION = Histogram(
    "astrofin_backtest_synthetic_duration_seconds", "Synthetic backtest duration",
    buckets=(0.1, 0.5, 1, 5, 10, 30),
)
AGENT_EXECUTION_COUNT = Counter(
    "astrofin_agent_execution_count_total", "Agent executions",
    ["agent_name"],
)
AGENT_EXECUTION_DURATION = Histogram(
    "astrofin_agent_execution_duration_seconds", "Agent async duration",
    ["agent_name"], buckets=(0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30),
)
AGENT_SELECTION_COUNTS = Counter(
    "astrofin_agent_selection_counts_total", "Agent selection by Thompson sampling",
    ["agent_name", "pool"],
)
THOMPSON_PARAMS = Gauge(
    "astrofin_thompson_params", "Thompson sampling params",
    ["agent_name", "param"],
)