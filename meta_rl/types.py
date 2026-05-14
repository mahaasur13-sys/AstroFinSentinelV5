"""meta_rl/types.py -- ATOM-META-RL-010: Common types for Meta-RL (Basket + BasketMetrics)"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class Signal(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class Regime(Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    NEUTRAL_R = "NEUTRAL"
    VOLATILE = "VOLATILE"


@dataclass
class EvaluationResult:
    """
    Immutable result of a strategy evaluation run.
    All fields are risk-aware. The reward pipeline MUST use
    risk_adjusted_pnl, not the raw pnl field.
    """
    pnl: float = 0.0
    sharpe: float = 0.0
    max_drawdown: float = 1.0
    trades: int = 0
    win_rate: float = 0.0
    execution_cost: float = 0.0
    risk_adjusted_pnl: float = 0.0
    risk_adjustment_reason: Optional[str] = None
    adjusted_drawdown: Optional[float] = None
    equity_curve: Optional[np.ndarray] = None
    overfit_report: Optional[Any] = field(default=None, repr=False)  # ATOM-META-RL-006

    def to_dict(self) -> dict:
        ec = self.equity_curve
        return {
            "pnl": self.pnl,
            "sharpe": self.sharpe,
            "max_drawdown": self.max_drawdown,
            "trades": self.trades,
            "win_rate": self.win_rate,
            "execution_cost": self.execution_cost,
            "risk_adjusted_pnl": self.risk_adjusted_pnl,
            "risk_adjustment_reason": self.risk_adjustment_reason,
            "adjusted_drawdown": self.adjusted_drawdown,
            "equity_curve": list(ec) if ec is not None else [],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EvaluationResult":
        ec = d.get("equity_curve", [])
        return cls(
            pnl=float(d.get("pnl", 0.0)),
            sharpe=float(d.get("sharpe", 0.0)),
            max_drawdown=float(d.get("max_drawdown", 1.0)),
            trades=int(d.get("trades", 0)),
            win_rate=float(d.get("win_rate", 0.0)),
            execution_cost=float(d.get("execution_cost", 0.0)),
            risk_adjusted_pnl=float(d.get("risk_adjusted_pnl", 0.0)),
            risk_adjustment_reason=d.get("risk_adjustment_reason"),
            adjusted_drawdown=float(d["adjusted_drawdown"]) if d.get("adjusted_drawdown") is not None else None,
            equity_curve=np.array(ec) if ec else None,
        )

    @classmethod
    def fail(cls) -> "EvaluationResult":
        return cls(
            pnl=0.0, sharpe=0.0, max_drawdown=1.0,
            trades=0, win_rate=0.0, execution_cost=0.0,
            risk_adjusted_pnl=0.0,
            risk_adjustment_reason="FAILSAFE",
            adjusted_drawdown=None,
            equity_curve=None,
        )


@dataclass
class ScoredStrategy:
    """Scored strategy after evaluation. Supports serialization."""
    strategy: Any
    reward: float
    generation: int = 1
    parent_ids: tuple = ()
    reward_history: List[float] = field(default_factory=list)
    evaluation: Optional[EvaluationResult] = None
    session_id: Optional[str] = None

    def to_dict(self) -> dict:
        eval_dict = self.evaluation.to_dict() if self.evaluation else {}
        return {
            "generation": self.generation,
            "parent_ids": list(self.parent_ids),
            "reward_history": list(self.reward_history),
            "evaluation": eval_dict,
            "reward": self.reward,
            "session_id": self.session_id or "",
        }


# ── ATOM-META-RL-010: Basket Metrics ─────────────────────────────────────────

@dataclass
class SymbolMetrics:
    """Per-symbol evaluation result inside a basket."""
    symbol: str
    pnl: float = 0.0
    sharpe: float = 0.0
    max_drawdown: float = 1.0
    trades: int = 0
    win_rate: float = 0.0
    exposure_pct: float = 0.0
    evaluation: Optional[EvaluationResult] = None

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "pnl": self.pnl,
            "sharpe": self.sharpe,
            "max_drawdown": self.max_drawdown,
            "trades": self.trades,
            "win_rate": self.win_rate,
            "exposure_pct": self.exposure_pct,
        }


@dataclass
class BasketMetrics:
    """
    ATOM-META-RL-010: Portfolio-level metrics across multiple assets.

    Aggregates per-symbol metrics with:
    - Total portfolio PnL (weighted)
    - Portfolio Sharpe ratio
    - Portfolio max drawdown
    - Correlation penalty (pairwise BTC/ETH/SPY)
    - Diversification bonus
    - Total active symbols
    """
    symbols: List[str]
    symbol_metrics: Dict[str, SymbolMetrics] = field(default_factory=dict)
    portfolio_pnl: float = 0.0
    portfolio_sharpe: float = 0.0
    portfolio_max_drawdown: float = 1.0
    correlation_penalty: float = 0.0
    diversification_bonus: float = 0.0
    active_symbols: int = 0
    portfolio_equity_curve: Optional[np.ndarray] = None

    def to_dict(self) -> dict:
        ec = self.portfolio_equity_curve
        return {
            "symbols": self.symbols,
            "symbol_metrics": {k: v.to_dict() for k, v in self.symbol_metrics.items()},
            "portfolio_pnl": round(self.portfolio_pnl, 6),
            "portfolio_sharpe": round(self.portfolio_sharpe, 4),
            "portfolio_max_drawdown": round(self.portfolio_max_drawdown, 6),
            "correlation_penalty": round(self.correlation_penalty, 6),
            "diversification_bonus": round(self.diversification_bonus, 6),
            "active_symbols": self.active_symbols,
            "portfolio_equity_curve": list(ec) if ec is not None else [],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BasketMetrics":
        ec_data = d.get("portfolio_equity_curve", [])
        symbol_metrics = {}
        for k, v in d.get("symbol_metrics", {}).items():
            symbol_metrics[k] = SymbolMetrics(
                symbol=v.get("symbol", k),
                pnl=float(v.get("pnl", 0.0)),
                sharpe=float(v.get("sharpe", 0.0)),
                max_drawdown=float(v.get("max_drawdown", 1.0)),
                trades=int(v.get("trades", 0)),
                win_rate=float(v.get("win_rate", 0.0)),
                exposure_pct=float(v.get("exposure_pct", 0.0)),
            )
        return cls(
            symbols=d.get("symbols", []),
            symbol_metrics=symbol_metrics,
            portfolio_pnl=float(d.get("portfolio_pnl", 0.0)),
            portfolio_sharpe=float(d.get("portfolio_sharpe", 0.0)),
            portfolio_max_drawdown=float(d.get("portfolio_max_drawdown", 1.0)),
            correlation_penalty=float(d.get("correlation_penalty", 0.0)),
            diversification_bonus=float(d.get("diversification_bonus", 0.0)),
            active_symbols=int(d.get("active_symbols", 0)),
            portfolio_equity_curve=np.array(ec_data) if ec_data else None,
        )
