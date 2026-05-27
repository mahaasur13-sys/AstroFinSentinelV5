"""meta_rl/intelligence/feedback_loop.py -- Meta-RL feedback loop"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class FeedbackEntry:
    strategy_id: str
    decision: str
    outcome: float
    regime: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    adjustment: Optional[dict] = None

class FeedbackLoop:
    def __init__(self, memory_size: int = 1000):
        self.memory_size = memory_size
        self.entries: list[FeedbackEntry] = []

    def record(self, strategy_id: str, decision: str, outcome: float, regime: str, adjustment: Optional[dict] = None):
        self.entries.append(FeedbackEntry(strategy_id, decision, outcome, regime, adjustment))
        if len(self.entries) > self.memory_size:
            self.entries = self.entries[-self.memory_size:]

    def get_regime_history(self, regime: str) -> list[FeedbackEntry]:
        return [e for e in self.entries if e.regime == regime]

    def get_adjustment_for(self, decision: str, regime: str) -> Optional[dict]:
        matches = [e for e in self.entries if e.decision == decision and e.regime == regime]
        adjustments = [e.adjustment for e in matches if e.adjustment]
        if not adjustments:
            return None
        return adjustments[-1]
