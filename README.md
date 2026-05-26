# 🧠 AstroFin Sentinel V5

**Multi-Agent Trading System with KARL Self-Improvement**

![Python](https://img.shields.io/badge/python-3.10+-green)
![Status](https://img.shields.io/badge/status-production--beta-blue)
![License](https://img.shields.io/badge/license-proprietary-red)

Мультиагентная торговая система, объединяющая фундаментальный, технический, макроэкономический и астрологический анализ для генерации торговых сигналов по криптовалютам.

---

## Возможности

| Модуль | Описание |
|--------|----------|
| **14 агентов** | Fundamental, Quant, Macro, Technical, Astro, Sentiment и др. |
| **Thompson Sampling** | Bayesian выбор агентов на основе belief tracking |
| **KARL AMRE** | Self-improvement loop с uncertainty quantification |
| **MAS Factory** | Динамическая оркестрация через topology |
| **Meta-Questioning** | Self-reflection для bias detection |
| **Astro-Timing** | Muhurta/Panchanga для optimal entry windows |
| **Meta-RL Engine** | Эволюция стратегий, reward shaping, cross-session replay |
| **Volatility Guards** | Динамический риск-менеджмент |

---

## Быстрый старт

```bash
# 1. Клонирование и установка
cd AstroFinSentinelV5
pip install -r requirements.txt

# 2. Настройка окружения
cp .env.example .env
# Заполни .env своими ключами (Binance, PostgreSQL и т.д.)

# 3. Базовая проверка (без реальных ключей)
python -m orchestration.sentinel_v5 "Analyze BTC" BTCUSDT SWING

# 4. С KARL self-improvement
python -m orchestration.karl_cli --diag

# 5. Dashboard (Dash/Plotly)
python web/app.py
# или в production:
gunicorn -w 4 -b 0.0.0.0:8050 web.wsgi:app
```

---

## Архитектура

```
User Query → Router → Parallel Agent Council → Synthesis
                              ↓
          ┌──────────────────┬┴──────────────┐
          ↓                  ↓               ↓
   ┌────────────┐    ┌────────────┐  ┌─────────────┐
   │Fundamental │    │   Macro    │  │   Quant     │
   │   20%      │    │    15%     │  │    20%      │
   └────────────┘    └────────────┘  └─────────────┘
          ↓                  ↓               ↓
   ┌────────────┐    ┌────────────┐  ┌─────────────┐
   │OptionsFlow │    │ Sentiment  │  │ Technical   │
   │    15%     │    │    10%     │  │    10%      │
   └────────────┘    └────────────┘  └─────────────┘
                              ↓
                    ┌──────────────────┐
                    │  KARL AMRE Loop   │
                    │ Self-improvement  │
                    └──────────────────┘
```

---

## Структура проекта

```
AstroFinSentinelV5/
├── meta_rl/              # Meta-RL Engine (6278 LOC)
│   ├── meta_agent.py     # MetaAgent с evolution
│   ├── persistence.py    # Session persistence
│   ├── strategy_pool.py  # Strategy pool management
│   ├── reward.py         # Reward shaping
│   ├── replay.py         # Cross-session replay
│   ├── evolution.py      # GA evolution loop
│   ├── walkforward.py    # Walk-forward validation
│   ├── ranking.py        # Strategy ranking
│   └── ...
├── agents/               # Multi-agent система
│   ├── _impl/           # Активные реализации
│   │   ├── fundamental_agent.py   # 20%
│   │   ├── quant_agent.py         # 20%
│   │   ├── macro_agent.py         # 15%
│   │   ├── options_flow_agent.py  # 15%
│   │   ├── sentiment_agent.py     # 10%
│   │   ├── technical_agent.py     # 10%
│   │   └── astro_council/         # Astro block (16%)
│   │       ├── agent.py           # AstroCouncilAgent
│   │       ├── bradley_agent.py   # 3%
│   │       ├── electoral_agent.py # 3%
│   │       ├── gann_agent.py      # 3%
│   │       ├── cycle_agent.py    # 5%
│   │       └── time_window_agent.py # 2%
│   └── _impl/amre/      # KARL AMRE Framework
│       ├── karl_integration.py
│       ├── grounding.py
│       ├── backtest_loop.py
│       └── ...
├── core/                 # Ядро
│   ├── ephemeris.py      # Swiss Ephemeris wrapper
│   ├── aspects.py        # Planetary aspects engine
│   ├── kepler.py         # Orbital mechanics
│   ├── volatility.py     # Volatility regime engine
│   ├── thompson.py       # Thompson Sampling
│   └── history_db.py     # Session persistence (SQLite)
├── orchestration/        # CLI и оркестрация
│   ├── sentinel_v5.py    # Основной entry point
│   ├── karl_cli.py       # KARL CLI (Rich UI)
│   └── router.py         # Query routing
├── web/                  # Dashboard
│   ├── app.py            # Dash app
│   ├── callbacks.py      # Dashboard callbacks
│   └── wsgi.py           # Gunicorn entry
├── backtest/
│   ├── engine.py         # Backtest engine
│   └── metrics_agent.py  # Metrics tracking (10 tests ✅)
├── trading/
│   └── execution/        # Execution bridges
│       └── twap.py       # TWAP executor
├── strategies/
│   └── generator.py      # Strategy generation
├── langgraph_schema.py   # LangGraph schema
├── muhurtha.py           # Muhurta timing
├── data_provider.py      # Data sources (CoinGecko, Binance)
└── pyproject.toml       # Project config
```

---

## Конфигурация

### `.env` (основной)

```bash
# Binance API (для live режима)
CCXT_API_KEY=your_binance_api_key_here
CCXT_API_SECRET=your_binance_api_secret_here
CCXT_SANDBOX_MODE=true        # Оставить true пока не протестируешь!
CCXT_LIVE_MODE=false
META_RL_LIVE_ENABLED=false
```

### `.env.db` (опционально — для PostgreSQL)

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=astrofin
POSTGRES_USER=astrofin
POSTGRES_PASSWORD=CHANGE_ME
REDIS_HOST=localhost
REDIS_PORT=6379
DB_BACKEND=postgresql   # или sqlite для dev
```

Без `.env.db` система использует SQLite (`core/history.db`, `core/belief.db`).

---

## Ключевые команды

```bash
# Анализ без KARL
python -m orchestration.sentinel_v5 "Analyze BTC" BTCUSDT SWING

# Анализ с KARL self-improvement
python -m orchestration.sentinel_v5 --karl "Analyze BTC" BTCUSDT SWING

# KARL CLI
python -m orchestration.karl_cli --diag
python -m orchestration.karl_cli --continuous BTCUSDT

# Dashboard (port 8050)
python web/app.py

# Тесты
python -m pytest backtest/test_metrics_agent.py -v
python -m pytest tests/test_kepler.py -v

# Установка как сервис (Zo)
# см. start-dashboard.sh и astrofin-dashboard.service
```

---

## Мета-RL движок

```python
from meta_rl.meta_agent import MetaAgent, EvolutionConfig

config = EvolutionConfig(
    population_size=20,
    elite_count=4,
    mutation_rate=0.15,
    crossover_rate=0.40,
)
agent = MetaAgent(config=config)
agent.initialize_population()
agent.evolve()
```

| Компонент | Файл | Описание |
|-----------|------|----------|
| `MetaAgent` | `meta_rl/meta_agent.py` | GA + Q-learning |
| `StrategyPool` | `meta_rl/strategy_pool.py` | Population management |
| `RewardCalculator` | `meta_rl/reward.py` | Reward shaping |
| `Persistence` | `meta_rl/persistence.py` | Session persistence |
| `ReplayBuffer` | `agents/_impl/amre/replay_buffer.py` | Experience replay |
| `WalkForward` | `meta_rl/walkforward.py` | Walk-forward analysis |
| `ABTesting` | `meta_rl/ab_testing.py` | A/B strategy comparison |

---

## Development

```bash
# Лinting
ruff check .
black --check .

# Type check
mypy . || true

# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
python -m pytest -v
```

---

## Roadmap

- [ ] Meta-RL-018: Production strategy discovery engine
- [ ] Real data APIs: Polygon, Unusual Whales, SEC EDGAR
- [ ] Telegram bot для alerts
- [ ] RAG index (FAISS/Chroma)
- [ ] PostgreSQL + TimescaleDB + pgvector migration
- [ ] Deployment: Kubernetes / Docker Compose# Test comment for CodeRabbit
