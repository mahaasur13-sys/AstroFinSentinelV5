from prometheus_client import Counter, Gauge, Histogram

## Counter: total number of strategies evaluated
strategies_evaluated = Counter("astrofin_strategies_evaluated_total", "Total number of strategy evaluations performed")

## Gauge: current number of active strategies in the pool
strategies_active = Gauge("astrofin_strategies_active", "Current number of active strategies in the pool")

## Histogram: duration of one generation of evolution (seconds)
evolution_duration_seconds = Histogram(
    "astrofin_evolution_duration_seconds",
    "Duration of evolution generation in seconds",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120),
)
