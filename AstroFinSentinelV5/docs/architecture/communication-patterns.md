# AstroFinSentinelV5 — Communication Patterns

**ATOM-META-RL-024 | Phase 2: Module Interaction Documentation**

This document describes all inter-module communication mechanisms, integration boundaries, and stateful components.

---

## 1. Shared-State Message Passing (LangGraph)

The primary orchestration pattern: a mutable `AgentState` dict flows through graph nodes. Each node reads/writes directly to this shared state.
Orchestration Layer ── AgentState TypedDict ──► Agent Layer
▲
└─── Reads/updates by all graph nodes
text


- **State keys:** `query`, `symbol`, `timeframe`, `selected_agents`, `agent_results`, `final_signal`, `risk_check`
- **File:** `langgraph_schema.py`, `orchestration/sentinel_v5.py`

---

## 2. Parallel Fan-Out (asyncio.gather)

Agents run simultaneously with exception isolation per agent.

┌───────────┐
│ Orchestrator│─── asyncio.gather ───┐
└───────────┘ │
┌──────────▼──────┐
│ Agent Pool │
│ ┌──┐ ┌──┐ ┌──┐│
│ │A1│ │A2│ │A3││
│ └──┘ └──┘ └──┘│
└─────────────────┘
text


- Each agent returns `AgentResponse`. On failure → NEUTRAL fallback.
- **Key location:** `agents/_impl/astro_council/agent.py` (`_run_sub_agents()`), flow runners in orchestration.

---

## 3. Thompson Sampling Gate

Probabilistic agent selection based on Beta(α,β) beliefs. Only agents above `min_usefulness` threshold participate.

BeliefTracker (SQLite) ──► ThompsonSampler.scores() ──► Selected agents
text


- **Gate:** `core/thompson.py` — `select()`, `scores()`
- **Config:** exploration bonus, `min_usefulness` threshold

---

## 4. Pressure Field Coordination

Agents adjust effective confidence based on neighbor agreement. This is currently feature-flagged off by default.

Agent_i.eff_conf = Agent_i.confidence * (1 + λ * Σ agreement_ij)
text


- **File:** `core/coordination/pressure_field.py`
- **Status:** off by default (flag: `ENABLE_PRESSURE_FIELD`)

---

## 5. Weighted Voting Council

Signals are aggregated using weighted voting: `Σ(signal_val × confidence × weight)`.

SynthesisAgent.council(inputs: List[AgentResponse]) → TradingSignal
text


- **File:** `core/council/council.py`, `agents/synthesis_agent.py`
- **Conflict resolution:** Astro vs Fundamental+Quant → Astro weight reduced by 30%

---

## 6. AMRE Audit Log

Passive blackboard for self-calibration. Read by `OAPOptimizer.sync_with_audit()`.

Decisions ──► AuditLog.record(DecisionRecord) ──► OAPOptimizer sync
text


- **File:** `agents/_impl/amre/audit.py`
- **Schema:** `DecisionRecord` with timestamp, state_hash, Q-values, final_action

---

## 7. Message Bus (MAS Factory)

Singleton publish/subscribe for dynamic topology execution.

MASFactoryArchitect ──► MessageBus.publish(topology) ──► TopologyExecutor
text


- **File:** `mas_factory/adapters.py`
- **Status:** experimental; topology caching (LRU, maxsize=32)

---

## Integration Boundaries Map

| Boundary | Contract | Status |
|----------|----------|--------|
| Orchestration ↔ Agents | `AgentState` dict → `AgentResponse` | ✅ Implemented |
| Agents ↔ Core | Read-only utilities (ephemeris, belief, reward) | ✅ Implemented |
| Meta-RL ↔ Core | `KARLState.oap_weights` → ThompsonSampler | ✅ Implemented |
| Trading ↔ Orchestration | `SafetyGate.check()` before broker | ✅ Implemented |
| Knowledge ↔ Agents | `RAGRetriever.retrieve()` → prompt context | ❌ Not wired |
| MAS Factory ↔ Orchestration | `MASFactoryArchitect.build()` → TopologyExecutor | ✅ Experimental |

---

## Stateful Components (Singletons)

| Component | Type | Location |
|-----------|------|----------|
| BeliefTracker | Module-level SQLite singleton | `core/belief.py` |
| ThompsonSampler | Double-checked locking singleton | `core/thompson.py` |
| Reward EMA | Module-level `_REWARD_EMA` | `core/reward_engine.py` |
| KARL Agent | Global `KARLSynthesisAgent` | `orchestration/karl_cli.py` |
| AuditLog | Singleton audit trail | `agents/_impl/amre/audit.py` |
| MessageBus | Singleton pub/sub | `mas_factory/adapters.py` |
| AgentRegistry | Singleton capability registry | `agents/gitagent_registry.py` |

---

## Thread Safety Notes

- ThompsonSampler and BeliefTracker are thread-safe.
- AuditLog writes are serial; reads are concurrent-safe.
- MessageBus is single-threaded in current implementation.
