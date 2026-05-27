"""meta_rl/intelligence/archetypes.py -- Strategy archetypes"""
from __future__ import annotations
from enum import Enum

class Archetype(Enum):
    TRENDFollower = "trend_follower"
    MEANReversion = "mean_reversion"
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING = "swing"

    def describe(self) -> str:
        desc = {
            Archetype.TRENDFollower: "Follows directional trends with trailing stops",
            Archetype.MEANReversion: "Bets on return to average after deviation",
            Archetype.MOMENTUM: "Captures continuation after strong moves",
            Archetype.BREAKOUT: "Enters on range-break confirmations",
            Archetype.SCALPING: "Fast small gains, high frequency",
            Archetype.SWING: "Multi-day swings, overnight holds",
        }
        return desc.get(self, "Unknown")

ARCHETYPE_TAGS = {
    "ma_cross": Archetype.TRENDFollower,
    "rsi_extreme": Archetype.MEANReversion,
    "volume_surge": Archetype.BREAKOUT,
    "high_freq": Archetype.SCALPING,
    "overnight_hold": Archetype.SWING,
}
