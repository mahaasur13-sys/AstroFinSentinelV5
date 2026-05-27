"""meta_rl/intelligence/self_questioning.py -- Self-questioning reflective agent"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Reflection:
    question: str
    answer: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class SelfQuestioning:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model
        self.history: list[Reflection] = []

    def reflect(self, observation: str, context: Optional[dict] = None) -> str:
        prompt = (
            f"Observation: {observation}
"
            "Generate a critical self-question and answer it briefly:
"
            "Q:"
        )
        # placeholder for Ollama call
        answer = f"[reflection based on: {observation[:50]}]"
        r = Reflection(question="Is this observation actionable?", answer=answer, confidence=0.7)
        self.history.append(r)
        return answer

    def get_insights(self) -> list[str]:
        return [f"Q: {r.question} → {r.answer[:80]}" for r in self.history[-5:]]
