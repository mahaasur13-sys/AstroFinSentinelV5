# Текущее состояние проекта

## ✅ Стабильные компоненты
- **Агенты:** 18 из 20 полностью реализованы.
- **RAG-ретривер:** FAISS-индексы для астрологии, технического анализа, трейдинга.
- **Мета-RL движок:** EvolutionEngine + walk-forward валидация.
- **KARL синтез:** 13-шаговый пайплайн с Q-обучением.
- **Risk Engine V2:** kill-switch, контроль экспозиции, корреляций.
- **Safety Gate:** композиция ModeEnforcer → RiskEngineV2 → SanityChecker.
- **CI/CD:** тесты, линтинг, покрытие (основа заложена).
- **Мониторинг:** Prometheus + Grafana + алерты.

## 🔨 В разработке (заглушки)
- `agents/_impl/macro_agent.py` — MacroAgent (возвращает NEUTRAL).
- `agents/_impl/astro_council/agent.py` — AstroCouncilAgent (заглушка).

## ⚠️ Ограничения
- `data/market_adapter.py` использует только синтетические OHLCV-данные.
- Астро-агенты зависят от эфемерид (требуется `pyswisseph`).

## 📊 Тестирование
- **241 тест** в 47 файлах.
- Покрытие: >80% для core (meta_rl, trading, agents).
- CI прогоняет юнит-тесты, но пока без PostgreSQL.

## 🔜 Ближайшие шаги
- Завершить MacroAgent и AstroCouncilAgent.
- Подключить живые рыночные данные (Binance).
- Добавить PostgreSQL в CI.
- Усилить безопасность и документирование.
