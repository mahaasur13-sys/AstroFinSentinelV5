"""meta_rl/lineage/experiment.py -- Experiment metadata"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Experiment:
    experiment_id: str
    name: str
    symbol: str
    timeframe: str
    population_size: int
    generations: int
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    finished_at: Optional[str] = None
    status: str = "running"  # running | completed | aborted
    best_strategy_id: Optional[str] = None
    config: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def finish(self, best_strategy_id: str):
        self.finished_at = datetime.utcnow().isoformat()
        self.status = "completed"
        self.best_strategy_id = best_strategy_id
