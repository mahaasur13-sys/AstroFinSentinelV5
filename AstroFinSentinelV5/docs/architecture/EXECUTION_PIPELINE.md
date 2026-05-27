# Execution Pipeline

## Pipeline Stages

### Stage 1 — Observation
Market OHLCV + indicators → `Observation` dataclass

### Stage 2 — Agent Analysis
Karl Agent + Synthesis Agent → `AgentDecision` (BUY/SELL/HOLD)

### Stage 3 — Meta-RL Evolution
Genetic algorithm: population=20, elite=2, mutation=0.1

### Stage 4 — Backtest Validation
Walk-forward: train=70%, test=30%, step=20%

### Stage 5 — Deployment
Top-3 strategies to production with risk limits
