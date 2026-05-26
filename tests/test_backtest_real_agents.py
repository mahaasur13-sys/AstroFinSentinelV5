import asyncio
import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from backtest.engine import BacktestEngine

@pytest.mark.asyncio
async def test_use_real_agents_does_not_generate_synthetic_signals():
    """При use_real_agents=True сигналы не должны содержать 'momentum=' из синтетического генератора."""
    engine = BacktestEngine(symbol="BTCUSDT", initial_capital=10000)
    
    # Подменяем агента, чтобы не зависеть от реальной реализации
    with patch('agents._impl.technical_agent.TechnicalAgent.run') as mock_run:
        mock_run.return_value = type('AgentResponse', (), {
            'signal': 'NEUTRAL',
            'confidence': 50,
            'reasoning': 'Technical indicators show no clear trend',
            'session_id': 'test-session',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })()
        
        result = await engine.run(
            start_date="2025-01-01",
            end_date="2025-01-10",
            use_real_agents=True
        )
        
        # Проверяем, что ни один сигнал не содержит "momentum="
        assert all("momentum=" not in t.signal_reasoning for t in result.trades), \
            "Real agents should not produce synthetic momentum signals"
        # Проверяем, что агент был вызван хотя бы раз
        assert mock_run.called, "Real agent was not called"
