# Dashboard Evaluation: LangGraph vs n8n for AstroFin Sentinel V5

**Date:** 2026-03-30
**ATOM:** ATOM-GITAGENT-002
**Status:** Recommended — **LangGraph** (primary), **n8n** (auxiliary)

---

## Executive Summary

**Recommendation:** Use **LangGraph** for MASFactory topology visualization, KARL metrics, and agent decision replay. Use **n8n** only for external event-driven integrations (Telegram alerts, email notifications, scheduled data collection pipelines).

LangGraph is the correct choice because AstroFin Sentinel V5's core workflow is a **cyclic computational graph** (agent nodes with weighted edges, KARL feedback loops, uncertainty-aware routing) — exactly what LangGraph is designed to model. n8n is a workflow automation tool for linear event sequences, not complex agent DAGs.

---

## LangGraph Evaluation

### Strengths for AstroFin Sentinel V5

| Capability | Fit | Notes |
|------------|------|-------|
| Cyclic graph topology | ✅ Perfect | LangGraph natively models MASFactory's multi-agent DAG with feedback |
| State management | ✅ Perfect | KARL state (uncertainty, trajectories, OAP) maps directly to LangGraph state |
| Agent orchestration | ✅ Strong | Parallel agent execution + conditional routing |
| Visualization | ✅ Strong | Built-in Mermaid/DOT export for topology graphs |
| Python-native | ✅ Perfect | AstroFin is Python-first; LangGraph integrates seamlessly |
| KARL integration | ✅ Strong | LangGraph's checkpointing maps to decision replay buffer |

### Integration Points

```python
# LangGraph would wrap MASFactory topology as:
from langgraph.graph import StateGraph
from astrofin.mas_factory.topology import Topology

def build_langgraph_from_topology(topology: Topology) -> StateGraph:
    """
    Convert MASFactory Topology → LangGraph StateGraph.
    Each Role becomes a graph node with conditional edges.
    """
    graph = StateGraph(AgentState)

    for role in topology.roles:
        graph.add_node(role.name, agent_node(role))

    for conn in topology.connections:
        graph.add_edge(conn.from_node, conn.to_node,
                       cond=conditional_function(conn))

    return graph.compile()
```

### Weaknesses

- **External integrations:** LangGraph has no built-in Telegram/email/webhook triggers
- **Learning curve:** Team needs LangChain/LangGraph familiarity
- **Visual dashboard:** Requires additional React/D3 layer on top of LangGraph

---

## n8n Evaluation

### Strengths

| Capability | Fit | Notes |
|------------|------|-------|
| External integrations | ✅ Strong | Telegram, email, Google Calendar, webhooks |
| Scheduled triggers | ✅ Strong | Cron-based data collection (e.g., every 15 min) |
| Linear workflows | ✅ Good | Data ingestion pipelines |
| No-code UI | ✅ Good | Non-technical team members can maintain |
| Zapier-like | ✅ Good | Quick automations without code |

### Weaknesses

| Capability | Fit | Notes |
|------------|------|-------|
| Complex agent graphs | ❌ Poor | n8n cannot model MASFactory's weighted agent topology |
| KARL state | ❌ Poor | No concept of uncertainty tracking or decision replay |
| Real-time decision making | ❌ Poor | n8n is pull-based (triggers), not push-based (agent loop) |
| Multi-agent orchestration | ❌ Poor | Single-flow workflow, not coordinated agent council |
| Python integration | ⚠️ Limited | Requires HTTP endpoints for Python agents |

### Use Cases for n8n (Auxiliary)

```yaml
# n8n workflows where it excels:

workflows:
  - data_collection:
      trigger: "schedule: */15 * * * *"
      steps:
        - HTTP Request → Binance OHLCV API
        - Transform → pandas DataFrame
        - Store → DuckDB

  - alert_dispatch:
      trigger: "webhook from AstroFin"
      steps:
        - Parse signal + confidence
        - If confidence > 80 → Telegram message
        - If signal == AVOID → Email alert

  - daily_report:
      trigger: "schedule: 0 9 * * *"
      steps:
        - Query KARL metrics from DB
        - Format Markdown
        - Send email digest
```

---

## Recommended Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ASTROFIN SENTINEL V5 — DASHBOARD STACK                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────────┐  │
│   │   Frontend     │      │   LangGraph     │      │       n8n          │  │
│   │   (React +     │◄────▶│   Core Engine   │      │   (Auxiliary)      │  │
│   │    D3.js)      │      │                 │      │                     │  │
│   │                 │      │  MASFactory     │      │  • Telegram Alerts │  │
│   │  • Topology     │      │  Topology       │      │  • Email Digests   │  │
│   │    Visualization│      │  KARL State     │      │  • Scheduled Data  │  │
│   │  • KARL Metrics │      │  Agent Council  │      │    Collection      │  │
│   │  • Decision     │      │  Weighted Vote  │      │  • Webhook Events  │  │
│   │    Replay       │      │                 │      │                     │  │
│   └─────────────────┘      └────────┬────────┘      └──────────┬──────────┘  │
│                                    │                           │              │
│                     ┌─────────────┴───────────────┐          │              │
│                     │         PostgreSQL +         │          │              │
│                     │       TimescaleDB +          │◄─────────┘              │
│                     │       pgvector               │                         │
│                     │                               │                         │
│                     │  • DecisionRecord (audit)     │                         │
│                     │  • KARL trajectories        │                         │
│                     │  • Agent state snapshots    │                         │
│                     │  • Market data               │                         │
│                     └─────────────────────────────┘                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Why |
|-----------|---------------|-----|
| **LangGraph** | Agent orchestration, KARL loop, topology execution | Core computational graph — LangGraph's sweet spot |
| **React + D3.js** | Topology visualization, KARL dashboard, decision replay | Interactive frontend for human analysis |
| **PostgreSQL + pgvector** | Persistent state, trajectory storage, similarity search | Relational + vector for RAG |
| **n8n** | External integrations (Telegram, email, scheduled tasks) | Event-driven automation, not core logic |
| **Zo Space** | Hosting for React dashboard | Managed, fast deployment |

---

## Implementation Roadmap

### Phase 1: LangGraph Integration (P1 — 2 weeks)
- [ ] Wrap `MASFactory.topology` as LangGraph `StateGraph`
- [ ] Map KARL state to LangGraph checkpointing
- [ ] Export topology visualization (Mermaid → D3.js)
- [ ] Build decision replay UI in React

### Phase 2: KARL Metrics Dashboard (P1 — 1 week)
- [ ] Connect decision audit trail to React dashboard
- [ ] Display uncertainty, confidence, OAP over time
- [ ] Show per-agent contribution weights

### Phase 3: n8n Auxiliary Workflows (P2 — 3 days)
- [ ] Telegram alert workflow (triggered by AstroFin webhook)
- [ ] Daily metrics email digest
- [ ] Scheduled OHLCV data collection pipeline

---

## Conclusion

**LangGraph** is the correct primary tool for AstroFin Sentinel V5's dashboard because:
1. The MASFactory topology is a **cyclic weighted DAG** — LangGraph's core abstraction
2. KARL state (uncertainty, trajectories, OAP) maps directly to **LangGraph checkpointing**
3. Python-native integration means no language barrier

**n8n** should be used only for peripheral concerns:
- External notifications (Telegram, email)
- Scheduled data collection
- Third-party integrations (Zapier-like)

The two tools are complementary: LangGraph owns the core agent loop, n8n handles the event-driven periphery.

---

*Generated by ATOM-GITAGENT-002 | AstroFin Sentinel V5*
