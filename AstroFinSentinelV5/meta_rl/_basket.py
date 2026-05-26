"""meta_rl/strategy_evaluator.py -- ATOM-META-RL-010: Add BasketEvaluator"""
from __future__ import annotations

import logging
from typing import Any, Optional

from meta_rl.backtest_adapter import BacktestEngineAdapter
from meta_rl.basket import MULTI_SYMBOL_ENABLED
from meta_rl.basket import BasketEvaluator as _BasketEvaluator
from meta_rl.types import BasketMetrics, EvaluationResult

logger = logging.getLogger(__name__)
MULTI_SYMBOL_ENABLED = True
RISK_INTEGRATION_ENABLED = True
KARL_META_UPDATE_ENABLED = True
WALK_FORWARD_ENABLED = True
EXECUTION_SANITY_ENABLED = True

class StrategyEvaluator:
    def __init__(
        self,
        backtest_adapter: Optional[BacktestEngineAdapter] = None,
        risk_engine: Any = None,
        sanity_checker: Any = None,
        use_sanity_check: bool = True,
    ):
        self.backtest_adapter = backtest_adapter or BacktestEngineAdapter(
            sanity_checker=sanity_checker if use_sanity_check else None,
            use_sanity_check=use_sanity_check,
        )
        self.risk_engine = risk_engine
        self.sanity_checker = sanity_checker
        self.use_sanity_check = use_sanity_check
        # ATOM-META-RL-010: Basket support
        self._basket_evaluator = None

    def _get_basket_evaluator(self) -> _BasketEvaluator:
        if self._basket_evaluator is None:
            self._basket_evaluator = _BasketEvaluator(
                strategy_evaluator=self,
                backtest_adapter=self.backtest_adapter,
                risk_engine=self.risk_engine,
            )
        return self._basket_evaluator

    def evaluate(
        self,
        strategy: Any,
        market_data: dict[str, Any],
    ) -> EvaluationResult:
        try:
            ohlcv = self._extract_ohlcv(market_data)
            if len(ohlcv) < 10:
                logger.warning("[META-RL] Not enough market data")
                return EvaluationResult.fail()
            result = self.backtest_adapter.run(strategy, ohlcv, market_data)
            if self.risk_engine is not None:
                result = self._apply_risk_engine(result, market_data)
            else:
                result = EvaluationResult(
                    pnl=result.pnl, sharpe=result.sharpe,
                    max_drawdown=result.max_drawdown, trades=result.trades,
                    win_rate=result.win_rate, execution_cost=result.execution_cost,
                    risk_adjusted_pnl=result.pnl, risk_adjustment_reason="NO_RISK_ENGINE",
                    adjusted_drawdown=result.max_drawdown,
                    equity_curve=result.equity_curve,
                )
            logger.debug(
                f"[META-RL] Evaluated: pnl={result.pnl:+.3f} "
                f"risk_adj={result.risk_adjusted_pnl:+.3f} "
                f"reason={result.risk_adjustment_reason} trades={result.trades}"
            )
            return result
        except Exception as e:
            logger.warning(f"[META-RL] Evaluation failed: {e}")
            return EvaluationResult.fail()

    def evaluate_basket(
        self,
        strategy: Any,
        market_data_dict: dict[str, dict],
    ) -> BasketMetrics:
        """
        ATOM-META-RL-010: Evaluate strategy across multiple assets.
        Delegates to BasketEvaluator for multi-symbol evaluation.
        Falls back gracefully if basket data is incomplete.
        """
        if not MULTI_SYMBOL_ENABLED:
            logger.warning("[META-RL] Multi-symbol disabled, using single-symbol")
            primary = list(market_data_dict.values())[0] if market_data_dict else {}
            result = self.evaluate(strategy, primary)
            # Convert single result to basket format
            from meta_rl.types import SymbolMetrics
            sm = SymbolMetrics(
                symbol=primary.get("symbol", "BTCUSDT") if isinstance(primary, dict) else "BTCUSDT",
                pnl=result.pnl, sharpe=result.sharpe,
                max_drawdown=result.max_drawdown,
                trades=result.trades, win_rate=result.win_rate,
                exposure_pct=1.0, evaluation=result,
            )
            return BasketMetrics(
                symbols=["BTCUSDT"],
                symbol_metrics={sm.symbol: sm},
                portfolio_pnl=result.pnl,
                portfolio_sharpe=result.sharpe,
                portfolio_max_drawdown=result.max_drawdown,
                active_symbols=1,
            )
        try:
            be = self._get_basket_evaluator()
            return be.evaluate_basket(strategy, market_data_dict)
        except Exception as e:
            logger.warning(f"[META-RL] Basket evaluation failed: {e}")
            return BasketMetrics(symbols=["BTCUSDT", "ETHUSDT", "SPY"])

    def evaluate_walk_forward(
        self,
        strategy: Any,
        market_data: dict[str, Any],
        n_splits: int = 3,
    ) -> EvaluationResult:
        if not WALK_FORWARD_ENABLED:
            return self.evaluate(strategy, market_data)
        try:
            splits = self.split_walk_forward(market_data, n_splits)
            if not splits:
                return self.evaluate(strategy, market_data)
            results = []
            for split in splits:
                split_data = {
                    **split,
                    "regime": market_data.get("regime", "NEUTRAL_R"),
                    "signal_strength": market_data.get("signal_strength", 50.0),
                    "momentum": market_data.get("momentum", 0.0),
                    "mean_reversion_signal": market_data.get("mean_reversion_signal", 0.0),
                    "atr": market_data.get("atr", market_data.get("close", 50000) * 0.02),
                    "symbol": market_data.get("symbol", "BTCUSDT"),
                }
                r = self.evaluate(strategy, split_data)
                results.append(r)
            return self._aggregate_results(results)
        except Exception as e:
            logger.warning(f"[META-RL] Walk-forward failed: {e}")
            return EvaluationResult.fail()

    def split_walk_forward(
        self,
        market_data: dict[str, Any],
        n_splits: int = 3,
    ) -> list[dict[str, Any]]:
        ohlcv = self._extract_ohlcv(market_data)
        if len(ohlcv) < 20:
            return []
        chunk = len(ohlcv) // n_splits
        if chunk < 10:
            return []
        splits = []
        for i in range(n_splits):
            start = i * chunk
            end = (i + 1) * chunk
            if end > len(ohlcv):
                break
            splits.append({"ohlcv": ohlcv[start:end]})
        return splits

    def _aggregate_results(self, results: list[EvaluationResult]) -> EvaluationResult:
        if not results:
            return EvaluationResult.fail()
        valid = [r for r in results if r.trades > 0]
        if not valid:
            return EvaluationResult.fail()
        import numpy as np
        return EvaluationResult(
            pnl=float(np.mean([r.pnl for r in valid])),
            sharpe=float(np.mean([r.sharpe for r in valid])),
            max_drawdown=float(np.mean([r.max_drawdown for r in valid])),
            trades=int(np.mean([r.trades for r in valid])),
            win_rate=float(np.mean([r.win_rate for r in valid])),
            execution_cost=float(np.mean([r.execution_cost for r in valid])),
            risk_adjusted_pnl=float(np.mean([r.risk_adjusted_pnl for r in valid])),
            risk_adjustment_reason="WALK_FORWARD_AGGREGATE",
            adjusted_drawdown=(
                float(np.mean([r.adjusted_drawdown for r in valid]))
                if all(r.adjusted_drawdown is not None for r in valid)
                else None
            ),
            equity_curve=None,
        )

    def _extract_ohlcv(self, market_data: dict[str, Any]) -> list:
        ohlcv = market_data.get("ohlcv", [])
        return ohlcv if isinstance(ohlcv, list) else []

    def _apply_risk_engine(
        self,
        result: EvaluationResult,
        market_data: dict,
    ) -> EvaluationResult:
        vol_regime = market_data.get("volatility_regime", "NORMAL")
        adj_pnl = self.risk_engine.adjust_pnl(
            result.pnl, result.max_drawdown, vol_regime,
        )
        dd_sq = result.max_drawdown ** 2
        adj_dd = max(0.0, result.max_drawdown - dd_sq)
        reason = f"KELLY_{vol_regime.upper()}_DD2"
        return EvaluationResult(
            pnl=result.pnl, sharpe=result.sharpe,
            max_drawdown=result.max_drawdown, trades=result.trades,
            win_rate=result.win_rate, execution_cost=result.execution_cost,
            risk_adjusted_pnl=adj_pnl,
            risk_adjustment_reason=reason,
            adjusted_drawdown=adj_dd,
            equity_curve=result.equity_curve,
        )
