import pytest
from unittest.mock import patch
from tools.metrics_server import AGENT_SELECTION_COUNTS

def test_agent_selection_increments_counter():
    """После выбора агентов через _select_for_flow счётчик должен инкрементироваться."""
    from orchestration.sentinel_v5 import _select_for_flow
    from core.thompson import TECHNICAL_POOL

    with patch('core.thompson.ThompsonSampler.select') as mock_select:
        mock_select.return_value = [("TechnicalAgent", 0.9)]
        _select_for_flow(TECHNICAL_POOL, k=1)

    # Проверяем, что значение дочернего счётчика стало > 0
    val = AGENT_SELECTION_COUNTS.labels(agent_name="TechnicalAgent", pool="technical")._value.get()
    assert val > 0, f"Expected counter > 0, got {val}"
