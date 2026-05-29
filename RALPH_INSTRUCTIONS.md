# Ralph Loop Instructions for AstroFin Sentinel V5

## Общие правила
- Работай СТРОГО над одной задачей из docs/tickets.md за итерацию.
- Перед началом прочитай progress.md, чтобы понять контекст.
- Всегда начинай с тестов (TDD).
- После реализации запусти `pytest` и `flake8 orchestration/`. Только если всё зелено — коммить.
- Используй conventional commits: feat:, fix:, test:, chore:.
- Обнови progress.md после завершения задачи.
- Не меняй docker-compose.yml, .env, core/tracing.py без явного указания в задаче.

## Обязательные проверки
- `pytest --cov --cov-report=term-missing`
- `flake8 orchestration/`
- `docker compose ps` (все сервисы должны быть healthy)

## Запрещено
- Коммитить в master (ты работаешь в отдельной ветке ralph-iteration-...).
- Пушить без зелёных тестов.
- Менять конфигурационные файлы без явной задачи.
