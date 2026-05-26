# AstroFinSentinelV5 — Improvement Recommendations

**ATOM-META-RL-024 | Phase 4: Architecture & Performance Recommendations**

This document provides structural, performance, scalability, and reliability recommendations for future development cycles.

---

## Modularity

1. **Extract AMRE** — Move `agents/_impl/amre/` (27 tightly coupled components) into a standalone top-level `amre/` module.
2. **Consolidate Councils** — Merge overlapping council implementations in `core/council/` and weighted voting in `SynthesisAgent`.
3. **Unified Broker Interface** — Create `trading/broker/` with factory pattern for multi-broker support (Binance, Kraken, Coinbase).
4. **Move Schema** — Move `langgraph_schema.py` from project root to `orchestration/schema.py` for logical grouping.

---

## Performance

1. **Ephemeris Caching** — Add LRU cache decorator to `calculate_natal_chart()` with 1-hour TTL (planetary positions change slowly).
2. **FAISS Preloading** — Load all domain indexes at startup in `RAGRetriever.__init__()` to eliminate per-query latency.
3. **Async SQLite** — Replace synchronous `BeliefTracker` with `aiosqlite` for compatibility with async orchestration paths.
4. **Batch Belief Updates** — Aggregate session results and batch-update `agent_beliefs` instead of per-agent writes.
5. **Connection Pool Monitoring** — Current PostgreSQL pool (5+10 overflow) is adequate; add metrics for connection health.

---

## Scalability

1. **Agent Isolation** — Run each agent pool in separate processes/containers; communicate via Redis or message queue.
2. **Read Replicas** — Add PostgreSQL read replicas for decision history queries; write only to primary.
3. **Topology Caching** — Current LRU cache (maxsize=32) in `ProductionMASEngine` is adequate; use Redis for distributed caching.
4. **Stateless Orchestration** — Move `ThompsonSampler` state to Redis; enable multiple orchestration instances.

---

## Reliability

1. **Circuit Breakers** — Implement circuit breaker pattern for `BinanceBroker` API calls to prevent cascade failures.
2. **Graceful Degradation** — If ephemeris unavailable, skip astro agents entirely (use neutral signal).
3. **Health Endpoint** — Add `/health` endpoint checking DB, broker, and Ollama connectivity.
4. **Structured Logging** — Add correlation IDs across all async flows for traceability.
