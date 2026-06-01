"""schema.py — Pydantic output schema for Insider"""

from pydantic import BaseModel, Field
from typing import List, Literal


class InsiderMetadata(BaseModel):
    features_used: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    uncertainty: float = Field(0.5, ge=0.0, le=1.0)
    karl_eligible: bool = Field(True)


class InsiderOutput(BaseModel):
    agent_name: str = Field(default="Insider")
    signal: Literal["LONG", "SHORT", "NEUTRAL", "AVOID"]
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str = Field(...)
    sources: List[str] = Field(default_factory=list)
    metadata: InsiderMetadata = Field(default_factory=InsiderMetadata)
