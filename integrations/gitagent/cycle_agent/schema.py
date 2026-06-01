"""schema.py — Pydantic output schema for Cycle"""

from pydantic import BaseModel, Field
from typing import List, Literal


class CycleMetadata(BaseModel):
    features_used: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    uncertainty: float = Field(0.5, ge=0.0, le=1.0)
    karl_eligible: bool = Field(True)


class CycleOutput(BaseModel):
    agent_name: str = Field(default="Cycle")
    signal: Literal["LONG", "SHORT", "NEUTRAL", "AVOID"]
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str = Field(...)
    sources: List[str] = Field(default_factory=list)
    metadata: CycleMetadata = Field(default_factory=CycleMetadata)
