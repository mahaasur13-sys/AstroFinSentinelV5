import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from backtest.engine import BacktestEngine


@pytest.mark.asyncio
async def test_use_real_agents_does_not_generate_synthetic_signals():
    """При use_real_agents=True сигналы не должны содержать 'momentum=' из синтетического генератора."""
    engine = BacktestEngine(symbol="BTCUSDT", initial_capital=10000)

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

        assert all("momentum=" not in t.signal_reasoning for t in result.trades), \
            "Real agents should not produce synthetic momentum signals"
        assert mock_run.called, "Real agent was not called"


@pytest.mark.asyncio
async def test_real_agent_backtest_generates_trades():
    """При use_real_agents=True backtest должен генерировать трейды с корректными сигналами."""
    engine = BacktestEngine(symbol="BTCUSDT", initial_capital=10000)
    with patch('agents._impl.technical_agent.TechnicalAgent.run') as mock_run:
        mock_run.return_value = type('AgentResponse', (), {
            'signal': 'LONG',
            'confidence': 75,
            'reasoning': 'RSI oversold, MACD bullish crossover',
            'session_id': 'test',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })()
        result = await engine.run("2025-01-01", "2025-01-10", use_real_agents=True)
        assert result is not None, "Backtest returned None"
        assert result.total_trades > 0, "Should generate at least one trade"
        for trade in result.trades:
            assert "momentum=" not in trade.signal_reasoning


@pytest.mark.asyncio
async def test_both_modes_return_same_structure():
    """Структура BacktestResult должна быть одинакова в обоих режимах."""
    engine = BacktestEngine(symbol="BTCUSDT", initial_capital=10000)

    with patch('agents._impl.technical_agent.TechnicalAgent.run') as mock_run:
        mock_run.return_value = type('AgentResponse', (), {
            'signal': 'NEUTRAL',
            'confidence': 50,
            'reasoning': 'No clear signal',
            'session_id': 'test',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })()

        result_real = await engine.run("2025-01-01", "2025-01-10", use_real_agents=True)
        result_synth = await engine.run("2025-01-01", "2025-01-10", use_real_agents=False)

    assert result_real is not None and result_synth is not None
    for field_name in ["total_trades", "win_rate", "sharpe_ratio", "max_drawdown_pct", "avg_confidence"]:
        assert getattr(result_real, field_name) is not None
        assert getattr(result_synth, field_name) is not None
    assert isinstance(result_real.total_trades, int)
    assert isinstance(result_synth.total_trades, int)


# ═══════════════════════════════════════════════════════════════════════════
# Срез 2: MacroAgent (падающий тест — добавить после реализации в engine)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_macro_agent_called_in_real_mode():
    """При use_real_agents=True должен вызываться MacroAgent."""
    engine = BacktestEngine(symbol="BTCUSDT", initial_capital=10000)
    with patch('agents._impl.macro_agent.MacroAgent.run') as mock_run:
        mock_run.return_value = type('AgentResponse', (), {
            'signal': 'NEUTRAL',
            'confidence': 50,
            'reasoning': 'Macro analysis: no clear trend',
            'session_id': 'test',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })()
        result = await engine.run("2025-01-01", "2025-01-10", use_real_agents=True)
        assert mock_run.called, "MacroAgent was not called"
