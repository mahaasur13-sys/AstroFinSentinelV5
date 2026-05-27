# Module Interaction Patterns

## meta_rl ↔ core
MetaAgent receives Observation from core.德性德

## meta_rl ↔ agents
MetaAgent invokes Karl via agents.karl_agent

## meta_rl ↔ trading
Backtester.run_walkforward() → EvaluationResult (Sharpe, Sortino, Calmar)

## web ↔ meta_rl
Dash callbacks read from MetaRLPersistence

## orchestration ↔ all
sentinel_v5.py LangGraph orchestrates all modules
