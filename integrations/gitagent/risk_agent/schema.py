"""schema.py — Pydantic output schema for Risk"""

from pydantic import BaseModel, Field
from typing import List, Literal


class RiskMetadata(BaseModel):
    features_used: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    uncertainty: float = Field(0.5, ge=0.0, le=1.0)
    karl_eligible: bool = Field(True)


class RiskOutput(BaseModel):
    agent_name: str = Field(default="Risk")
    signal: Literal["LONG", "SHORT", "NEUTRAL", "AVOID"]
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str = Field(...)
    sources: List[str] = Field(default_factory=list)
    metadata: RiskMetadata = Field(default_factory=RiskMetadata)
