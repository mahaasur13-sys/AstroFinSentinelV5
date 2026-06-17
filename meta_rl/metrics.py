"""
AstroFin Sentinel V5 — Prometheus Metrics

Single source of truth for all Prometheus metrics in the system.
Both `meta_rl` and `tools/metrics_server.py` import from here.

Conventions:
    - All metric names prefixed with `astrofin_`
    - Counters use `_total` suffix
    - Histograms use `_seconds` for durations
    - Gauges use no suffix
"""

from prometheus_client import Counter, Gauge, Histogram

# ═════════════════════════════════════════════════════════════════════════════
# EvolutionEngine metrics
# ═════════════════════════════════════════════════════════════════════════════

EVOLUTION_RUNS = Counter(
    "astrofin_evolution_runs",
    "Total evolution runs started",
)
STRATEGIES_EVALUATED = Counter(
    "astrofin_evolution_strategies_evaluated",
    "Total strategies evaluated",
)
GENERATION_CURRENT = Gauge(
    "astrofin_evolution_generation_current",
    "Current generation number",
)
STRATEGY_EVALUATED_TOTAL = Counter(
    "astrofin_evolution_strategy_evaluated_total",
    "Total strategies evaluated across all runs",
)
BEST_REWARD = Gauge(
    "astrofin_evolution_best_reward",
    "Best reward in current generation",
)
MEAN_REWARD = Gauge(
    "astrofin_evolution_mean_reward",
    "Mean reward of population",
)
REWARD_STD = Gauge(
    "astrofin_evolution_reward_std",
    "Standard deviation of reward",
)
POPULATION_SIZE = Gauge(
    "astrofin_evolution_population_size",
    "Current population size",
)
STRATEGIES_CREATED = Counter(
    "astrofin_evolution_strategies_created",
    "Total strategies created",
)
GENERATIONS_TOTAL = Counter(
    "astrofin_evolution_generations_total",
    "Total number of generations",
)
GENERATION_DURATION = Histogram(
    "astrofin_evolution_generation_duration_seconds",
    "Duration of each generation in seconds",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120),
)
EVOLUTION_DURATION = Histogram(
    "astrofin_evolution_duration_seconds",
    "Duration of evolution generation in seconds",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120),
)
STRATEGIES_ACTIVE = Gauge(
    "astrofin_evolution_strategies_active",
    "Current number of active strategies in the pool",
)

# ═════════════════════════════════════════════════════════════════════════════
# Backtest metrics (moved from tools/metrics_server.py)
# ═════════════════════════════════════════════════════════════════════════════

BACKTEST_REAL_RUNS = Counter(
    "astrofin_backtest_real_runs",
    "Real data backtest runs",
)
BACKTEST_SYNTHETIC_RUNS = Counter(
    "astrofin_backtest_synthetic_runs",
    "Synthetic data backtest runs",
)
BACKTEST_FAILURES = Counter(
    "astrofin_backtest_failures",
    "Backtest runs that failed (exceptions, timeouts)",
)
BACKTEST_DURATION = Histogram(
    "astrofin_backtest_duration_seconds",
    "Backtest execution duration in seconds",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 300),
)
BACKTEST_SYMBOLS_TRADED = Counter(
    "astrofin_backtest_symbols_traded",
    "Total symbols traded across all backtests",
    ["symbol"],
)

# ═════════════════════════════════════════════════════════════════════════════
# Agent execution metrics
# ═════════════════════════════════════════════════════════════════════════════

AGENT_DURATION = Histogram(
    "astrofin_agent_duration_seconds",
    "Agent execution duration in seconds",
    ["agent", "status"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)
AGENT_CALLS = Counter(
    "astrofin_agent_calls",
    "Total agent invocations",
    ["agent", "status"],
)
AGENT_DEGRADED = Counter(
    "astrofin_agent_degraded",
    "Number of times an agent returned a degraded response (UNKNOWN/EPHEMERIS_UNAVAILABLE)",
    ["agent", "reason"],
)
AGENT_SELECTION_COUNTS = Counter(
    "astrofin_agent_selection_counts",
    "Agent selection counts (Thompson Sampling picks)",
    ["agent", "pool"],
)
AGENT_BELIEF_ALPHA = Gauge(
    "astrofin_agent_belief_alpha",
    "Beta(alpha, beta) alpha parameter per agent",
    ["agent"],
)
AGENT_BELIEF_BETA = Gauge(
    "astrofin_agent_belief_beta",
    "Beta(alpha, beta) beta parameter per agent",
    ["agent"],
)

# ═════════════════════════════════════════════════════════════════════════════
# Thompson Sampling metrics
# ═════════════════════════════════════════════════════════════════════════════

THOMPSON_PARAMS = Gauge(
    "astrofin_thompson_params",
    "Thompson Sampling parameters (alpha, beta) per agent",
    ["agent", "param"],
)
THOMPSON_SELECTIONS = Counter(
    "astrofin_thompson_selections",
    "Number of Thompson sampling selections per pool",
    ["pool"],
)
THOMPSON_FALLBACKS = Counter(
    "astrofin_thompson_fallbacks",
    "Number of times Thompson sampling fell back to a random agent (no eligible)",
    ["pool", "reason"],
)

# ═════════════════════════════════════════════════════════════════════════════
# RAG / data_room metrics
# ═════════════════════════════════════════════════════════════════════════════

CACHE_HITS = Counter(
    "astrofin_cache_hits",
    "Cache hits",
)
CACHE_MISSES = Counter(
    "astrofin_cache_misses",
    "Cache misses",
)
OLLAMA_STATUS = Gauge(
    "astrofin_ollama_status",
    "Ollama service status (1=healthy, 0=down)",
)
RAG_CHUNK_COUNT = Gauge(
    "astrofin_rag_chunk_count",
    "Number of chunks in RAG index",
)
RAG_QUERY_CACHE_HITS = Counter(
    "astrofin_rag_query_cache_hits",
    "RAG query cache hits",
)
RAG_QUERY_CACHE_MISSES = Counter(
    "astrofin_rag_query_cache_misses",
    "RAG query cache misses",
)
RAG_RELEVANCE_SCORE = Histogram(
    "astrofin_rag_relevance_score",
    "Relevance score of RAG chunks",
    buckets=(0.1, 0.3, 0.5, 0.7, 0.9, 1.0),
)
DATA_ROOM_CONFLICTS_UNRESOLVED = Gauge(
    "data_room_conflicts_unresolved",
    "Number of unresolved Data Room conflicts",
)
DATA_ROOM_LAST_INVENTORY_UPDATE = Gauge(
    "data_room_last_inventory_update",
    "Unix timestamp of last Data Room inventory update",
)
# KARL / OAP / Drift / Risk / Meta-RL — alert-targeted metrics
OOS_FAIL_RATE = Gauge("astrofin_oos_fail_rate", "OOS fail rate (alert > 0.4)")
KARL_DRIFT_DETECTED = Gauge("astrofin_karl_drift_detected", "1 if KARL detected drift")
META_RL_WIN_RATE = Gauge("astrofin_meta_rl_win_rate", "Meta-RL win rate (alert < 0.45)")
DRAWDOWN_PERCENT = Gauge("astrofin_drawdown_percent", "Drawdown (alert > 0.08)")
KARL_QSTAR_MEAN = Gauge("astrofin_karl_qstar_mean", "Mean Q*")
DRIFT_SCORE = Gauge("astrofin_drift_score", "OAP drift score")
