from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
import time


@dataclass
class EvaluationResult:
    pnl: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    fitness: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class Signal:
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class Strategy:
    id: str
    params: dict
    generation: int = 0
    parent_ids: tuple = field(default_factory=tuple)
    fitness: float = 0.0
    result: Optional[EvaluationResult] = None

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SymbolMetrics:
    win_rate: float = 0.0
    exposure_pct: float = 0.0
    evaluation: Optional['EvaluationResult'] = None

@dataclass
class BasketMetrics:
    symbols: list = field(default_factory=list)
    symbol_metrics: dict = field(default_factory=dict)
    portfolio_pnl: float = 0.0
    portfolio_sharpe: float = 0.0
    portfolio_max_drawdown: float = 0.0
    active_symbols: int = 0
