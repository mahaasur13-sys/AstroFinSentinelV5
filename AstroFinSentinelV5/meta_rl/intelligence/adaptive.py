"""meta_rl/intelligence/adaptive.py -- Adaptive agent selection"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import random

@dataclass
class AgentPerformance:
    agent_id: str
    wins: int = 0
    trials: int = 0
    avg_reward: float = 0.0

    @property
    def win_rate(self) -> float:
        return self.wins / max(self.trials, 1)

    def record(self, reward: float, win: bool):
        self.trials += 1
        self.avg_reward = (self.avg_reward * (self.trials - 1) + reward) / self.trials
        if win:
            self.wins += 1

class AdaptiveSelector:
    def __init__(self, agents: list[str], epsilon: float = 0.1):
        self.agents = agents
        self.epsilon = epsilon
        self.performance: dict[str, AgentPerformance] = {a: AgentPerformance(a) for a in agents}

    def select(self) -> str:
        if random.random() < self.epsilon:
            return random.choice(self.agents)
        return max(self.performance, key=lambda a: self.performance[a].win_rate)

    def record(self, agent_id: str, reward: float, win: bool):
        self.performance[agent_id].record(reward, win)

    def state(self) -> dict:
        return {a: vars(p) for a, p in self.performance.items()}
