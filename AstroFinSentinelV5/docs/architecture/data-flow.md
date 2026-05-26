# AstroFinSentinelV5 — Data Flow Diagrams

**ATOM-META-RL-024 | Phase 1: Architecture Documentation**

This document describes the complete lifecycle of a trading signal through the system, the reward feedback loop, and the meta-learning flow.

---

## 1. Request Flow — End-to-End Signal Generation
User Query
│
▼
router.py ─────────────────────────────────────────────────────┐
│ RouterOutput │
▼ │
ThompsonSampler ─── BeliefTracker (SQLite) │
│ selected_agents │
▼ │
┌───────────────────────────────────────────────────────┐ │
│ Parallel Flows (asyncio.gather) │ │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐ │ │
│ │Technical│ │ Macro │ │ Astro │ │ Electoral │ │ │
│ │ Flow │ │ Flow │ │ Flow │ │ Flow │ │ │
│ └────┬────┘ └────┬────┘ └────┬────┘ └──────┬───────┘ │ │
│ └───────────┴───────────┴─────────────┘ │ │
└───────────────────────────┬───────────────────────────┘ │
▼ │
SynthesisAgent / KARLSynthesisAgent │
│ │
▼ │
┌─────────────────┐ │
│ SafetyGate │ │
│ ┌─────────────┐ │ │
│ │ModeEnforcer │ │ │
│ │RiskEngineV2 │ │ │
│ │SanityChecker│ │ │
│ └─────────────┘ │ │
└────────┬────────┘ │
▼ │
BinanceBroker (CCXT) ◄───────────────────────┘
│
▼
TWAP/VWAP Executor
text


### Steps

1. **User Query** enters through CLI (`orchestration/karl_cli.py`) or future REST API.
2. **Router** (`orchestration/router.py`) determines intent, domain, and agent pools.
3. **ThompsonSampler** (`core/thompson.py`) selects the most promising agents based on Beta(α,β) belief distributions stored in `core/belief.db`.
4. **Parallel Flows** execute specialist agents simultaneously via `asyncio.gather()`. Each agent returns an `AgentResponse`.
5. **Synthesis** layer (SynthesisAgent or KARLSynthesisAgent) aggregates signals using weighted voting, resolves conflicts, and produces a final `TradingSignal`.
6. **SafetyGate** (`trading/safety_gate.py`) applies mode enforcement, risk checks (`RiskEngineV2`), and sanity validation.
7. **BinanceBroker** places the order, and execution algorithms (TWAP/VWAP) handle slicing.

---

## 2. Feedback Loop — Belief Update Cycle

Trade Outcome
│
▼
Reward Pipeline ─────────────── compute_reward_pipeline()
│
▼
BeliefTracker ───────────────── update(agent_name, reward)
│ ↓
│ Beta(α+success, β+failure)
│
▼
ThompsonSampler ────────────── updated priors influence next selection
text


### Steps

1. After order execution, the **Reward Pipeline** (`core/reward_engine.py`) computes a scalar reward based on PnL, signal quality, and risk-adjusted return.
2. **BeliefTracker** (`core/belief.py`) updates the Beta distribution for each agent involved.
3. The updated beliefs become new priors for the **ThompsonSampler**, closing the loop and adapting future agent selection.

---

## 3. Meta-RL Flow — Evolutionary Improvement

Session Results (N decisions)
│
▼
KARLState ──────────────────── aggregate oap_weights, uncertainty, drift
│
▼
Evolution Engine ──────────── genetic operators (mutation, crossover, elite selection)
│
▼
StrategyPool ──────────────── store elite strategies, discard weak ones
│
▼
OAP Optimizer ─────────────── tune online adaptive parameters
│
▼
ThompsonSampler ───────────── receive updated OAP weights
text


### Steps

1. **Session Results** from multiple decisions are collected in `meta_rl/replay.py`.
2. **KARLState** analyzes the aggregated performance, detecting drift and adjusting uncertainty.
3. **Evolution Engine** (`meta_rl/evolution.py`) runs a genetic algorithm to produce new candidate strategies.
4. **StrategyPool** (`meta_rl/strategy_pool.py`) stores promising strategies, replacing underperformers.
5. **OAP Optimizer** adjusts online adaptive parameters like exploration rate and TTC depth.
6. The new OAP weights are fed back to the ThompsonSampler, influencing future agent selection.

---

## Summary

These three flows operate continuously:

- **Request Flow** runs per user query.
- **Feedback Loop** runs per trade outcome.
- **Meta-RL Flow** runs asynchronously over multiple sessions.

Together they enable autonomous, self-improving trading decisions.
