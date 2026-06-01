"""schema.py — Pydantic output schema for Elliot"""

from pydantic import BaseModel, Field
from typing import List, Literal


class ElliotMetadata(BaseModel):
    features_used: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    uncertainty: float = Field(0.5, ge=0.0, le=1.0)
    karl_eligible: bool = Field(True)


class ElliotOutput(BaseModel):
    agent_name: str = Field(default="Elliot")
    signal: Literal["LONG", "SHORT", "NEUTRAL", "AVOID"]
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str = Field(...)
    sources: List[str] = Field(default_factory=list)
    metadata: ElliotMetadata = Field(default_factory=ElliotMetadata)
