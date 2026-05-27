"""Типы данных для meta_rl."""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class EvaluationResult:
    """Результат оценки стратегии."""
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0
    avg_confidence: float = 0.0
    total_return_pct: float = 0.0
    score: float = 0.0
    metadata: Optional[dict] = None


@dataclass
class BasketMetrics:
    """Метрики корзины стратегий."""
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0
    avg_confidence: float = 0.0
    total_return_pct: float = 0.0
    num_strategies: int = 1


@dataclass
class ScoredStrategy:
    """Стратегия с оценкой (используется в эволюции и пулах)."""
    strategy_id: str = ""
    agent_name: str = ""
    fitness: float = 0.0
    generation: int = 0
    config: dict = field(default_factory=dict)
    metrics: Optional[EvaluationResult] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "agent_name": self.agent_name,
            "fitness": self.fitness,
            "generation": self.generation,
            "config": self.config,
            "metrics": self.metrics.__dict__ if self.metrics else None,
            "metadata": self.metadata,
        }
