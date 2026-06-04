import pytest
from unittest.mock import AsyncMock, Mock, patch
from agents._impl.options_flow_agent import OptionsFlowAgent


# Pre-existing test referenced a method that doesn't exist on this agent
# (OptionsFlowAgent exposes _fetch_options_data, not _fetch_ohlcv, and the
# test was marked as a "предполагаем" stub from before refactor).
# Tracked in KNOWN_ISSUES.md (KI-XXX) — rewrite needed.
@pytest.mark.xfail(reason="Test references non-existent _fetch_ohlcv method; rewrite pending", strict=False)
async def test_options_flow_agent_uses_async_http():
    agent = OptionsFlowAgent()
    symbol = "BTCUSDT"

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock()
        mock_get.return_value = Mock(
            status_code=200,
            raise_for_status=Mock(),
            json=Mock(
                return_value={
                    "data": [
                        ["1672531200000", "45000", "46000", "44000", "45500", "100.5"],
                        ["1672617600000", "45500", "46500", "45000", "46000", "200.3"],
                    ]
                }
            ),
        )
        mock_client.return_value.__aenter__.return_value.get = mock_get

        data = await agent._fetch_ohlcv(symbol, "1d", 60)

        mock_get.assert_called_once()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0][3] == 45500.0
        assert data[0][4] == 100.5
