# AstroFinSentinelV5 — Component Catalog

**ATOM-META-RL-024 | Phase 1: Architecture Documentation**

This catalog documents all seven major subsystems: their responsibilities, public interfaces, dependencies, configuration, and failure modes.

---

## 1. Presentation Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | User interaction, CLI command intake, operational visibility |
| **Public Interface** | `orchestration/karl_cli.py` (CLI), Dash web app (`web/app.py`), future REST API |
| **Dependencies** | Orchestration Layer (router, sentinel_v5) |
| **Configuration** | `.env` for API keys; gunicorn config for dashboard |
| **Failure Modes** | CLI exits gracefully on errors; dashboard reports 500 with health endpoint |

---

## 2. Orchestration Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Request routing, Thompson agent selection, parallel execution, flow coordination |
| **Public Interface** | `orchestration/sentinel_v5.py`, `orchestration/sentinel_v5_mas.py`, `orchestration/router.py` |
| **Dependencies** | Core Services (thompson, belief), Agent Layer, Trading Layer |
| **Configuration** | Exploration bonus, default_k, pool definitions |
| **Failure Modes** | Failed agents return NEUTRAL; unresponsive flows have 30s timeout; all errors logged to history |

---

## 3. Agent Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Signal generation, domain specialization, synthesis and consensus |
| **Public Interface** | `BaseAgent.run(state) → AgentResponse`, `SynthesisAgent.synthesize(responses) → TradingSignal` |
| **Dependencies** | Core Services (ephemeris, aspects, belief), Data Layer (RAG retrieval - planned) |
| **Configuration** | `config/agent_weights.yaml` or inline `HYBRID_WEIGHTS` dict |
| **Failure Modes** | Exceptions in agents caught with NEUTRAL fallback; stale agent produces low-confidence signal |

### Agent Weight Table (from config/agent_weights.yaml)

| Category | Weight | Agents |
|----------|--------|--------|
| Fundamental | 20% | FundamentalAgent |
| Quant | 20% | QuantAgent, MLPredictorAgent |
| Options | 15% | OptionsFlowAgent |
| Macro | 15% | MacroAgent |
| Technical | 10% | TechnicalAgent, MarketAnalyst, ElliotAgent |
| Sentiment | 10% | SentimentAgent, BullResearcher, BearResearcher |
| Astro | 10% | GannAgent, BradleyAgent, CycleAgent, TimeWindowAgent, ElectoralAgent, MuhurtaAgent |

---

## 4. Core Services Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Deterministic shared computations: ephemeris, belief tracking, reward calculation, coordination |
| **Public Interface** | `core/ephemeris.py`, `core/belief.py`, `core/thompson.py`, `core/reward_engine.py`, `core/council/` |
| **Dependencies** | Swiss Ephemeris library, SQLite |
| **Configuration** | Orb definitions in `core/aspects.py`, reward function weights |
| **Failure Modes** | Ephemeris unavailable → simplified calculations; BeliefTracker uses thread-safe singleton; ThompsonSampler returns uniform when no data |

---

## 5. Meta-Learning Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Strategy evolution, online adaptive parameter tuning, long-term learning |
| **Public Interface** | `meta_rl/meta_agent.py` (MetaAgent), `meta_rl/evolution.py` (GA), `meta_rl/persistence.py` (Persistence) |
| **Dependencies** | Core Services (Thompson, Reward), Data Layer (session storage) |
| **Configuration** | `meta_rl/config.py` (population size, mutation rate, crossover rate) |
| **Failure Modes** | Evolution stalls → fallback to elite strategies; OAP drift detection triggers rollback |

---

## 6. Trading Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Execution safety, risk management, broker communication, order management |
| **Public Interface** | `trading/safety_gate.py`, `trading/risk_v2.py`, `trading/execution/twap.py` |
| **Dependencies** | Broker adapter (BinanceBroker via CCXT), Orchestration Layer (for signal input) |
| **Configuration** | Position limits, leverage caps, correlation thresholds, kill switches |
| **Failure Modes** | Risk check fails → order rejected; broker timeout → retry with backoff; kill switch → immediate halt |

---

## 7. Data Layer

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Persistence, retrieval, vector search, session storage |
| **Public Interface** | `db/`, `knowledge/` (FAISS indexes, RAG retriever) |
| **Dependencies** | PostgreSQL/SQLite, FAISS, Redis (planned) |
| **Configuration** | `.env.db` for PostgreSQL connection; FAISS index paths |
| **Failure Modes** | DB unavailable → fallback to SQLite; FAISS unavailable → no retrieval (agents use generic prompts) |

---

## Summary

All seven layers interact through well-defined contracts:

- **Presentation → Orchestration**: CLI/REST calls
- **Orchestration → Agents**: State dict + AgentResponse
- **Agents → Core**: Read-only shared services
- **Meta-RL → Core**: OAP weight feedback
- **Trading → Broker**: Abstracted adapter
- **Data → Agents**: Retrieval interface (partially implemented)
