"""Prometheus metrics for AstroFin Meta-RL.

Single source of truth — imported by both metrics_server.py (exposition)
and evolution.py / agent.py (recording). All share the default REGISTRY.
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