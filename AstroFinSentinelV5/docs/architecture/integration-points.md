# AstroFinSentinelV5 — Integration Points

**ATOM-META-RL-024 | Phase 2: Module Interaction Documentation**

This document maps all integration boundaries between modules, their contracts, and current implementation status.

---

## Orchestration ↔ Agents

| Attribute | Value |
|-----------|-------|
| **Contract** | `AgentState` dict (input) → `AgentResponse` (output) |
| **Method** | Each agent implements `run(state)` returning `AgentResponse` |
| **Status** | ✅ Fully implemented |

---

## Agents ↔ Core Services

| Attribute | Value |
|-----------|-------|
| **Contract** | Read-only utility calls: ephemeris, aspects, belief tracking |
| **Method** | `BeliefTracker` provides Thompson priors; `compute_reward_pipeline()` for feedback |
| **Status** | ✅ Fully implemented |

---

## Meta-RL ↔ Core

| Attribute | Value |
|-----------|-------|
| **Contract** | `KARLState.oap_weights` → `ThompsonSampler` |
| **Method** | `set_external_karl_feedback(q_star, regime)` updates sampler parameters |
| **Status** | ✅ Implemented |

---

## Trading ↔ Orchestration

| Attribute | Value |
|-----------|-------|
| **Contract** | `SafetyGate.check()` called before `BinanceBroker.place_order()` |
| **Method** | Orchestration calls safety gate; only on pass proceeds to broker |
| **Status** | ✅ Fully implemented |

---

## Knowledge ↔ Agents (RAG)

| Attribute | Value |
|-----------|-------|
| **Contract** | `RAGRetriever.retrieve(query) → List[KnowledgeChunk]` |
| **Method** | `retrieve_knowledge()` defined in `knowledge/rag_retriever.py` but no agent imports it |
| **Status** | ❌ Not wired — critical gap |

---

## MAS Factory ↔ Orchestration

| Attribute | Value |
|-----------|-------|
| **Contract** | `MASFactoryArchitect.build() → Topology`; `TopologyExecutor.run(topology)` |
| **Method** | `orchestration/sentinel_v5_mas.py` calls architect and executor |
| **Status** | ✅ Experimental (topology caching active) |

---

## Summary

All critical integration paths are functional except the RAG system, which is implemented but not connected to agent prompts. This is the highest-priority remediation item.
