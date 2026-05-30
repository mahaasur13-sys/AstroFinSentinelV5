# Dashboard Evaluation: LangGraph vs n8n

**Проект:** AstroFinSentinelV5 — MASFactory Topology & KARL Metrics Visualization
**Дата:** 2026-03-29
**Автор:** ATOM-GITAGENT-003

---

## 1. Executive Summary

| Критерий | LangGraph | n8n |
|----------|-----------|-----|
| **Сложность интеграции** | Средняя | Низкая |
| **Визуализация топологии** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **KARL метрики** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Production readiness** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Стоимость** | Бесплатно (self-hosted) | Freemium / ~€20/мес |
| **Мой вердикт** | ✅ Рекомендую | Не рекомендую для этой задачи |

**Рекомендация:** Использовать **LangGraph + custom viz** для MASFactory topology и KARL метрик.

---

## 2. LangGraph

### 2.1 Что это

LangGraph — это библиотека для построения **cyclic graphs** (циклических графов) поверх LangChain. Используется для multi-agent систем с feedback loops. Идеально подходит для MASFactory.

### 2.2 Преимущества для AstroFin

**✅ LangGraph的优点:**

1. **Cyclic graphs** — MASFactory использует SwitchNode с feedback, LangGraph原生支持 циклы
2. **State management** — Встроенный `StateGraph` для передачи состояния между агентами
3. **Replay** — `LangGraph.checkpointer` позволяет воспроизводить любой путь выполнения (идеально для KARL trajectory replay)
4. **Visualization** — `get_graph()` + Mermaid export для topology visualization
5. **Type safety** — Pydantic states, полная типизация
6. **MASFactory совместимость** — можно обернуть MASFactory topology в LangGraph без переписывания

```python
# Пример: MASFactory topology → LangGraph
from langgraph.graph import StateGraph, END
from mas_factory.topology import Topology

def masfactory_to_langgraph(topology: Topology) -> StateGraph:
    graph = StateGraph(MASState)

    for role in topology.roles:
        graph.add_node(role.name, masfactory_role_executor(role))

    for conn in topology.connections:
        graph.add_edge(conn.from_node, conn.to_node)

    return graph.compile()
```

### 2.3 KARL Metrics Visualization

```python
# LangGraph + KARL dashboard
def visualize_karl_metrics(checkpoint: Checkpoint):
    """Визуализация KARL decision chain."""
    graph = get_graph()

    # Highlight nodes by uncertainty
    for node in graph.nodes:
        kpi = get_karl_kpi(node.state)
        color = uncertainty_to_color(kpi.uncertainty_total)
        node.style = {"fill": color}

    return graph.draw_mermaid()
```

### 2.4 Недостатки

- **Кривая обучения** — требует понимания graph programming
- **No built-in UI** — нужно строить свой frontend или использовать LangServe
- **Debugging** — verbose, сложные stack traces при ошибках

### 2.5 Стоимость

- **Self-hosted:** бесплатно (Apache 2.0)
- **LangSmith:** ~$39/мес (для observability)
- **LangServe:** бесплатно (self-hosted)

---

## 3. n8n

### 3.1 Что это

n8n — это **low-code workflow automation platform** с визуальным drag-and-drop редактором. Работает как Zapier, но с возможностью self-hosting.

### 3.2 Преимущества

1. **Low-code** — можно быстро прототипировать
2. **Visual editor** — drag-and-drop workflow
3. **Many integrations** — 400+ интеграций
4. **Self-hosted** — бесплатно

### 3.3 Недостатки для AstroFin

**❌ n8n的缺点:**

1. **Не подходит для cyclic graphs** — n8n это DAG (directed acyclic graph), не поддерживает циклы без костылей
2. **Agentic workflows** — n8n это workflow automation, не multi-agent system
3. **Custom logic** — KARL metrics, Thompson Sampling, AMRE — всё это невозможно выразить в n8n визуально
4. **No state management** — между запусками нет persistence
5. **MASFactory несовместимость** — n8n не может обернуть Python-агенты без написания custom nodes

### 3.4 Когда использовать n8n

n8n **подходит** для:
- Оркестрация внешних API (CoinGecko, Binance)
- Уведомления (Telegram, Email)
- Scheduled data collection
- Простые webhook workflows

### 3.5 Стоимость

- **Cloud:** ~€20/мес (Pro)
- **Self-hosted:** бесплатно (MIT)
- **Enterprise:** Custom pricing

---

## 4. Рекомендуемая архитектура

### 4.1 Для MASFactory Topology

```python
# LangGraph visualization pipeline
from langgraph.visualizer import visualize_topology
import json

def export_topology_for_dashboard(topology: Topology):
    """Экспорт MASFactory topology в формат для dashboard."""

    # 1. LangGraph
    graph = masfactory_to_langgraph(topology)

    # 2. Mermaid diagram
    mermaid = graph.get_graph().draw_mermaid()

    # 3. Interactive D3.js visualization
    nodes = []
    edges = []
    for role in topology.roles:
        nodes.append({
            "id": role.name,
            "label": role.name,
            "type": role.agent_type,
            "weight": role.weight,
        })
    for conn in topology.connections:
        edges.append({
            "source": conn.from_node,
            "target": conn.to_node,
        })

    return {
        "mermaid": mermaid,
        "d3": {"nodes": nodes, "edges": edges},
        "metadata": {
            "intention": topology.intention,
            "version": topology.version,
            "roles_count": len(topology.roles),
        }
    }
```

### 4.2 Для KARL Metrics

```python
# KARL metrics → Grafana/Prometheus
def export_karl_metrics(karl_state: KPIControlState) -> Dict:
    """Экспорт KARL KPIs в Prometheus format."""

    metrics = {
        # OAP metrics
        f"karl_oap_ttc_depth": karl_state.current_ttc_depth,
        f"karl_oap_exploration": karl_state.current_exploration_rate,
        f"karl_oap_grounding": karl_state.current_grounding_strength,

        # Regime stability
        f"karl_uncertainty_total": karl_state.uncertainty_avg,
        f"karl_entropy": karl_state.entropy_avg,
        f"karl_oos_fail_rate": karl_state.oos_fail_rate,

        # Rewards
        f"karl_reward_ema": karl_state.reward_state.ema_reward,
    }

    return metrics  # Push to Prometheus/Grafana
```

### 4.3 Dashboard Stack

```
┌─────────────────────────────────────────────────┐
│                  Frontend                          │
│   React + D3.js (topology) + Recharts (metrics)  │
└────────────────────────┬────────────────────────┘
                         │ HTTP API
┌────────────────────────▼────────────────────────┐
│              LangServe / FastAPI                │
│   MASFactory ↔ LangGraph ↔ KARL State          │
└────────────────────────┬────────────────────────┘
                         │ Metrics
┌────────────────────────▼────────────────────────┐
│         Prometheus + Grafana                    │
│   Real-time KARL KPIs + Decision traces         │
└─────────────────────────────────────────────────┘
```

---

## 5. Сравнительная таблица

| Функция | LangGraph | n8n | verdict |
|---------|-----------|-----|---------|
| Cyclic graphs | ✅ Полная | ⚠️ Limited | LangGraph |
| Agent workflows | ✅ Да | ⚠️ Basic | LangGraph |
| Topology viz | ✅ Mermaid + custom | ⚠️ Built-in | LangGraph (custom) |
| KARL metrics | ✅ Direct | ❌ Невозможно | LangGraph |
| Replay/debug | ✅ Checkpointer | ⚠️ Basic | LangGraph |
| Self-hosted | ✅ | ✅ | Оба |
| Learning curve | ⚠️ Средняя | ✅ Низкая | n8n (для простых задач) |
| Production | ✅ | ✅ | Оба |
| Custom logic | ✅ Python | ⚠️ JS/Node | LangGraph |
| Cost | ✅ Free | ⚠️ €20/мес | LangGraph |

---

## 6. Рекомендация

### Для AstroFinSentinelV5: **LangGraph**

**Почему:**
1. MASFactory = cyclic multi-agent system → LangGraph natively supports this
2. KARL metrics требуют custom Python logic → n8n не справится
3. Decision replay → LangGraph checkpointer = идеально
4. Topology visualization → LangGraph → Mermaid → Custom D3.js
5. Полная совместимость с MASFactory (обёртка в 50 строк)

**Roadmap:**
1. **Q2 2026:** Обёртка `masfactory_to_langgraph()` (ATOM-VIZ-001)
2. **Q2 2026:** KARL metrics → Prometheus exporter (ATOM-VIZ-002)
3. **Q3 2026:** React dashboard с D3.js topology + Recharts metrics (ATOM-VIZ-003)
4. **Q4 2026:** LangServe deployment (ATOM-VIZ-004)

**Когда использовать n8n:**
- Внешние интеграции (Telegram alerts, email notifications)
- Scheduled data collection от API
- Простые webhook workflows

**n8n НЕ подходит для:**
- MASFactory topology
- KARL AMRE loop
- Agent decision chains
- Thompson Sampling visualization
- Any cyclic agentic logic
