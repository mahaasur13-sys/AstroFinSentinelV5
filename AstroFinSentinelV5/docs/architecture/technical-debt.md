# AstroFinSentinelV5 — Technical Debt Register

**ATOM-META-RL-024 | Phase 3: Technical Debt and Risk Analysis**

This document tracks known technical debt, prioritised by impact, with concrete remediation steps.

---

## Critical Priority

| # | Issue | Impact | Location | Remediation |
|---|-------|--------|----------|-------------|
| 1 | **RAG System Not Wired** | HIGH — agents cannot access grounding knowledge | `knowledge/rag_retriever.py` defines `retrieve_knowledge()` but no agent imports it | Wire `RAGRetriever.retrieve()` into `BaseAgent._build_prompt()`; add fallback for Ollama unavailability |
| 2 | **Backtest Engine Decoupled** | HIGH — backtests use synthetic signals, not real MAS agents | `backtest/engine.py` | Add `use_real_agents=True` mode; inject MAS signals instead of synthetic |
| 3 | **Dual Persistence Systems** | MEDIUM — `MetaRLPersistence` and `VersionedEliteStorage` overlap | `meta_rl/persistence.py`, `meta_rl/versions_storage.py` | Deprecate `VersionedEliteStorage`; migrate to unified `MetaRLPersistence` API |

---

## High Priority

| # | Issue | Impact | Location | Remediation |
|---|-------|--------|----------|-------------|
| 4 | **Duplicate Type Definitions** | MEDIUM — `AgentResponse` defined in both `core/base_agent.py` and `agents/_impl/types.py` | Two files | Keep only `core/base_agent.py`; update imports |
| 5 | **Scattered Feature Flags** | MEDIUM — env vars across `coordination/constants.py`, `meta_rl/config.py`, `safety_gate.py` | Multiple files | Create unified `config/feature_flags.yaml` with schema validation |
| 6 | **Hard-coded Agent Pool Mappings** | LOW — `_POOL_MAP` in `belief.py` duplicates `thompson.py` | `core/belief.py`, `core/thompson.py` | Single source of truth in `core/thompson.py` |

---

## Medium Priority

| # | Issue | Impact | Location | Remediation |
|---|-------|--------|----------|-------------|
| 7 | **No Graceful Degradation for Ollama** | MEDIUM — RAG retrieval fails hard if Ollama unavailable | `knowledge/rag_retriever.py` | Add try/except with fallback to generic prompt |
| 8 | **Synchronous SQLite in Async Context** | LOW — potential blocking in async orchestration paths | `core/belief.py` | Replace with `aiosqlite` |
| 9 | **Uncached Ephemeris Calls** | LOW — `calculate_natal_chart()` recalculates on every call | `core/ephemeris.py` | Add LRU cache with 1-hour TTL |

---

## Summary

- **Critical items (1-3):** Should be addressed in the next development cycle (Q1).
- **High items (4-6):** Plan for Q2.
- **Medium items (7-9):** Continuous improvement during regular development.
