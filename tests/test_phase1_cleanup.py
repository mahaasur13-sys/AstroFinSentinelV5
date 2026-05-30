"""Smoke-тесты для Phase 1: базовые импорты после очистки."""

import pytest


def test_core_imports():
    from core.auth import fastapi_require_api_key, require_api_key
    from core.logging import setup_logging
    from core.metrics import track_agent_duration
    from core.tracing import setup_tracing


def test_orchestration_import():
    from orchestration.sentinel_v5 import run_sentinel_v5


def test_monitoring_import():
    from deploy.monitoring.health_endpoints import app


def test_web_import():
    from web.wsgi import server


def test_no_dead_imports():
    """Убедимся, что удаляемые модули действительно не импортируются."""
    with pytest.raises(ImportError):
        from web.middleware import auth  # уже не должно существовать
    with pytest.raises(ImportError):
        from meta_rl import _basket
