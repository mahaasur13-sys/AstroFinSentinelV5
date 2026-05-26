# Q1 Priorities — Foundation Hardening

**ATOM-META-RL-024 | Phase 5: Development Roadmap**

---

## Weeks 1-2: Foundation Hardening

- Wire RAG system into agent prompts via `BaseAgent._build_prompt()`
- Consolidate `AgentResponse` type definitions (keep only `core/base_agent.py`)
- Create unified `config/feature_flags.yaml` with schema validation
- Add health endpoint checking DB, broker, and Ollama connectivity

## Weeks 3-4: Backtest Integration

- Add `use_real_agents=True` mode to `BacktestEngine`
- Implement signal injection interface for MAS → backtest
- Create backtest validation suite comparing synthetic vs real signals

## Weeks 5-6: Observability

- Add Prometheus metrics: agent selection rates, signal distribution, latency percentiles
- Implement structured logging with correlation IDs across async flows
- Create Grafana dashboards for real-time monitoring

## Weeks 7-8: Risk Engine Hardening

- Add unit tests for all `RiskEngineV2` edge cases (NaN handling, boundary conditions)
- Implement circuit breaker for broker API calls
- Add position reconciliation check between internal state and broker
