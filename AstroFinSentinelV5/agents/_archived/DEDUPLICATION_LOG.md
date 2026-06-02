# DEDUP-001 + Dual-Mode Test Fix — Итоговый отчёт

**Дата:** 2026-03-29 (финальный)
**Статус:** ✅ ЗАВЕРШЕНО
**Атом:** ATOM-DEDUP-001 (P0) + ATOM-FIX-DUALMODE
**Выполнено:** Zo Agent

---

## 1. Дедупликация агентов

### Ситуация до начала работ
- 7 агентов (`fundamental_agent`, `macro_agent`, `quant_agent`, `options_flow_agent`, `sentiment_agent`, `bull_researcher`, `bear_researcher`) — **уже отсутствовали** в `agents/`
- `agents/synthesis_agent.py` (20,947 B) — **уже перемещён** в `_archived/` ранее
- Импорты — **все уже указывали** на `agents._impl.*`

### Структура после DEDUP

```
agents/
├── __init__.py              ✅ Пустой (ambiguity prevention)
├── astro_council_agent.py  ✅ Сохранён (stub-wrapper, D2-решение)
├── base_agent.py           ✅ Сохранён (re-export: core.base_agent + types.Signal)
├── karl_synthesis.py       ✅ Сохранён (отдельная KARL-система)
├── _archived/              ✅ 4 stub-файла + DEDUPLICATION_LOG.md
│   ├── electoral_agent.py   (112 B, stub)
│   ├── market_analyst.py    (111 B, stub)
│   ├── synthesis_agent.py   (20,947 B, полный дубликат)
│   ├── technical_agent.py   (112 B, stub)
│   └── DEDUPLICATION_LOG.md
└── _impl/                  ✅ КАНОНИЧЕСКИЙ (22 агента)
```

### Импорты обновлены (7 файлов)

| Файл | Импорт | Статус |
|------|--------|--------|
| `agents/astro_council_agent.py` | `agents._impl.synthesis_agent` | ✅ Исправлен |
| `agents/karl_synthesis.py` | `agents._impl.synthesis_agent` | ✅ Исправлен |
| `orchestration/sentinel_v5_mas.py` | `agents._impl.synthesis_agent` | ✅ Исправлен |
| `langgraph_schema.py` | `agents._impl.*` | ✅ Был исправлен |
| `tests/test_orchestrator.py` | `agents._impl.*` | ✅ Исправлен |
| `backtest/atom_014_stress_test.py` | `agents._impl.synthesis_agent` | ✅ Был исправлен |
| `agents/_impl/__init__.py` | Экспорт SynthesisAgent, TechnicalAgent и др. | ✅ Исправлен |

---

## 2. Фикс dual-mode теста

### Проблема
```
AttributeError: module 'orchestration' has no attribute 'sentinel_v5_mas'
ImportError: cannot import name 'TopologyExecutor' from 'mas_factory.engine'
ImportError: cannot import name 'get_meta_questioning_engine' from 'mas_factory'
```

### Исправления

**`orchestration/__init__.py`** (создан):
```python
"""orchestration — AstroFin Sentinel v5 orchestration layer."""
from __future__ import annotations
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration import sentinel_v5
    from orchestration import sentinel_v5_mas

def __getattr__(name: str):
    if name == "sentinel_v5_mas":
        import orchestration.sentinel_v5_mas
        return orchestration.sentinel_v5_mas
    if name == "sentinel_v5":
        import orchestration.sentinel_v5
        return orchestration.sentinel_v5
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**`mas_factory/__init__.py`** (добавлен экспорт):
```python
# Было:
from mas_factory.engine import ProductionMASEngine, MASFactoryConfig, get_production_engine
__all__ = [..., "TopologyVisualizer"]

# Стало:
from mas_factory.engine import (ProductionMASEngine, MASFactoryConfig,
                                get_production_engine, TopologyExecutor)
__all__ = [..., "TopologyExecutor", "TopologyVisualizer"]
```

**`mas_factory/engine.py`** (добавлен alias):
```python
# Alias for backward compatibility
TopologyExecutor = ProductionMASEngine
```

**`orchestration/sentinel_v5_mas.py`** (исправлен импорт):
```python
# Было:
from mas_factory import get_meta_questioning_engine as get_meta_questioning

# Стало:
from agents._impl.amre.meta_questioning import get_meta_engine as get_meta_questioning
```

---

## 3. Результаты тестов

| Набор | До | После |
|-------|-----|-------|
| `pytest tests/` | 39 passed, 1 failed | **40 passed** ✅ |
| `test_dual_mode.py` | 4 passed, 1 failed | **5 passed** ✅ |

---

## 4. Канонический импорт

```python
# ✅ ПРАВИЛЬНО:
from agents._impl import FundamentalAgent, MacroAgent, QuantAgent
from agents._impl.synthesis_agent import SynthesisAgent

# ❌ БОЛЬШЕ НЕ СУЩЕСТВУЕТ:
from agents.fundamental_agent import FundamentalAgent
from agents.synthesis_agent import SynthesisAgent
```

---

## 5. Следующие ATОМы

| Приоритет | АТОМ | Зависимость | Описание |
|-----------|------|-------------|----------|
| 🔴 P0 | `ATOM-DB-MIGRATION` | DEDUP-001 ✅ | SQLite → PostgreSQL + TimescaleDB + pgvector |
| 🟡 P1 | `ATOM-GITAGENT-003` | DEDUP-001 ✅ | GitAgent: автогенерация commit messages |
| 🟡 P1 | `ATOM-RAG-001` | DEDUP-001 ✅ | RAG index (FAISS/Chroma) |
| 🟢 P2 | `ATOM-TELEGRAM-001` | DEDUP-001 ✅ | Telegram бот для alerts |
