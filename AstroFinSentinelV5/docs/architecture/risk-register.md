# AstroFinSentinelV5 — Risk Register

**ATOM-META-RL-024 | Phase 3: Systemic Risks**

This document identifies risks that could impact system reliability, scalability, or correctness.

---

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Single Broker Dependency** | HIGH — no alternative if Binance API fails | MEDIUM | Add broker abstraction with multi-broker support (Kraken, Coinbase) |
| **Memory Leak in KARLState** | HIGH — could degrade performance over time | LOW | Fixed via bounded deques (audited 2026-05-15); monitor via metrics |
| **Thompson Sampling Cold Start** | MEDIUM — uniform priors for new agents may cause poor initial selections | HIGH | Increase exploration bonus for new agents; consider warm-up period |
| **Correlation Concentration** | MEDIUM — RiskEngineV2 uses 0.80 threshold, may allow clustered positions | MEDIUM | Lower correlation threshold to 0.70; add sector-based grouping |
| **Feature Flag Proliferation** | MEDIUM — 15+ env vars with no central docs or validation | HIGH | Consolidate into `config/feature_flags.yaml` with validation |
| **Async/Sync Boundary Issues** | MEDIUM — `asyncio.gather()` calling sync DB operations could deadlock | MEDIUM | Audit all sync calls in async paths; convert to async where needed |

---

## Monitoring and Review

- All risks should be reviewed quarterly.
- Add automated checks for correlation thresholds and memory usage.
- Risk register updates are part of the regular release cycle.
