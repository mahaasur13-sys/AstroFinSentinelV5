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

def test_signal_distribution_increments():
    """При получении сигнала от агента счётчик распределения должен инкрементироваться."""
    from tools.metrics_server import AGENT_SIGNAL_DISTRIBUTION
    import asyncio
    from orchestration.sentinel_v5 import run_technical_flow
    from unittest.mock import patch

    # Мокаем run_market_analyst, чтобы вернуть LONG
    async def mock_run(state):
        from agents.base_agent import AgentResponse, SignalDirection
        resp = AgentResponse(
            agent_name="MarketAnalyst", signal=SignalDirection.LONG,
            confidence=75, reasoning="Bullish"
        )
        return {"marketanalyst_signal": resp.to_dict()}

    with patch('orchestration.sentinel_v5.run_market_analyst', side_effect=mock_run):
        state = {"symbol": "BTCUSDT", "current_price": 50000}
        asyncio.run(run_technical_flow(state))

    # Проверяем, что счётчик для MarketAnalyst и LONG увеличился
    val = AGENT_SIGNAL_DISTRIBUTION.labels(agent_name="MarketAnalyst", signal="LONG")._value.get()
    assert val > 0, f"Expected signal distribution counter > 0, got {val}"
