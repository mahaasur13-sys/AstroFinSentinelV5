# AstroFinSentinelV5 — State Management

**ATOM-META-RL-024 | Phase 2: Stateful Components Documentation**

This document catalogues all singletons and stateful components, ensuring thread-safety awareness.

---

## Singleton Components

| Component | Location | Thread-Safe | Notes |
|-----------|----------|-------------|-------|
| **BeliefTracker** | `core/belief.py` | Yes | SQLite-backed, module-level singleton |
| **ThompsonSampler** | `core/thompson.py` | Yes | Double-checked locking singleton |
| **Reward EMA** | `core/reward_engine.py` | No | Module-level `_REWARD_EMA`, single-writer |
| **KARLSynthesisAgent** | `orchestration/karl_cli.py` | Yes | Global singleton, state protected by locks |
| **AuditLog** | `agents/_impl/amre/audit.py` | Yes | Singleton, writes serial, reads concurrent |
| **MessageBus** | `mas_factory/adapters.py` | No | Singleton, single-threaded (current) |
| **AgentRegistry** | `agents/gitagent_registry.py` | Yes | Capability registry, read-heavy |

---

## State Lifecycle

1. **Initialization**: BeliefTracker loads from SQLite on first access. ThompsonSampler is created with default exploration bonus.
2. **Update**: Beliefs updated after each trade outcome via `tracker.update()`. KARLState evolves asynchronously.
3. **Shutdown**: No explicit cleanup needed — SQLite WAL handles crash safety.

---

## Synchronization Notes

- All concurrent agent runs (`asyncio.gather`) read beliefs without locks.
- Belief writes are serialized by SQLite transactions.
- AuditLog writes are protected by a mutex; reads are lock-free.
