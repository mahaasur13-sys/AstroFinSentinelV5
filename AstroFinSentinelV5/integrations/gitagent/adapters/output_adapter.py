"""adapters/output_adapter.py — ATOM-GITAGENT-005: Unified Output Adapter
Обеспечивает консистентный output contract ВСЕХ агентов.
Применяется ПОСЛЕ registry.run() — единая точка нормализации.
"""
import logging
from dataclasses import dataclass
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# ─── Signal Normalization ─────────────────────────────────────────────────────

SIGNAL_ALIASES = {
    # Variations → canonical
    "STRONG_BUY": "BUY", "STRONG_LONG": "LONG", "BUY": "BUY",
    "LONG": "BUY",
    "STRONG_SELL": "SELL", "STRONG_SHORT": "SHORT", "SELL": "SELL",
    "SHORT": "SELL",
    "HOLD": "NEUTRAL", "NEUTRAL": "NEUTRAL", "AVOID": "AVOID",
    "bullish": "BUY", "bearish": "SELL",
    "positive": "BUY", "negative": "SELL",
    "up": "BUY", "down": "SELL",
    "long": "BUY", "short": "SELL",
}

SIGNAL_PRIORITY = {"BUY": 1, "SELL": -1, "NEUTRAL": 0, "AVOID": -2}

def normalize_signal(value: Any) -> str:
    """Convert any signal representation to canonical form."""
    if value is None:
        return "NEUTRAL"
    s = str(value).strip().upper()
    # Direct match
    if s in SIGNAL_ALIASES:
        return SIGNAL_ALIASES[s]
    # Fuzzy match
    for canonical, _ in SIGNAL_ALIASES.items():
        if canonical in s or s in canonical:
            return SIGNAL_ALIASES[canonical]
    # Unknown → NEUTRAL
    logger.warning(f"[OutputAdapter] Unknown signal: {value!r} → NEUTRAL")
    return "NEUTRAL"


def normalize_confidence(value: Any) -> int:
    """Ensure confidence is int 0–100."""
    if value is None:
        return 50
    try:
        conf = float(value)
    except (TypeError, ValueError):
        logger.warning(f"[OutputAdapter] Invalid confidence: {value!r} → 50")
        return 50
    # Clamp to 0–100
    return max(0, min(100, int(round(conf))))


# ─── Main Adapter ─────────────────────────────────────────────────────────────

@dataclass
class NormalizedOutput:
    """Canonical output contract for ALL agents."""
    signal: str           # BUY | SELL | NEUTRAL | AVOID
    confidence: int        # 0–100
    reasoning: str         # Human-readable explanation
    metadata: dict         # Agent-specific data
    agent_name: str        # Which agent produced this
    raw_output: dict       # Original output for debugging

    def to_dict(self) -> dict:
        return {
            "signal": self.signal,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "agent_name": self.agent_name,
        }

    def is_directional(self) -> bool:
        return self.signal in ("BUY", "SELL")

    def is_bullish(self) -> bool:
        return self.signal == "BUY"

    def is_bearish(self) -> bool:
        return self.signal == "SELL"

    def is_avoid(self) -> bool:
        return self.signal == "AVOID"

    def confidence_level(self) -> str:
        """Human-readable confidence band."""
        if self.confidence >= 80:
            return "HIGH"
        elif self.confidence >= 60:
            return "MEDIUM"
        elif self.confidence >= 40:
            return "LOW"
        return "VERY_LOW"


class UnifiedOutputAdapter:
    """
    Применяется ВСЕГДА после registry.run(agent_name, input).
    
    Responsibilities:
    1. Signal normalization (все варианты → BUY/SELL/NEUTRAL/AVOID)
    2. Confidence normalization (0–100, int)
    3. Metadata preservation
    4. Reasoning extraction
    5. Compatibility mode для агентов без metadata
    """

    def __init__(self, strict: bool = False):
        self.strict = strict

    def adapt(
        self, raw_output: Any, agent_name: str, agent_capabilities: Optional[dict] = None
    ) -> NormalizedOutput:
        """
        Main entry point — convert any agent output to NormalizedOutput.
        """
        # ── Dict or object? ────────────────────────────────────────────────
        if isinstance(raw_output, dict):
            data = raw_output
        elif hasattr(raw_output, "to_dict"):
            data = raw_output.to_dict()
        elif hasattr(raw_output, "__dict__"):
            data = vars(raw_output)
        else:
            logger.warning(f"[OutputAdapter] Unknown output type {type(raw_output)}: wrapping as NEUTRAL")
            data = {}

        # ── Extract fields with fallbacks ────────────────────────────────────
        raw_signal = data.get("signal") or data.get("direction") or data.get("action") or "NEUTRAL"
        raw_confidence = data.get("confidence") or data.get("score") or data.get("conf") or 50
        reasoning = data.get("reasoning") or data.get("explanation") or data.get("text") or ""
        metadata = data.get("metadata") or data.get("extra") or {}

        # ── Normalize ────────────────────────────────────────────────────────
        signal = normalize_signal(raw_signal)
        confidence = normalize_confidence(raw_confidence)

        # ── Confidence adjustment based on capabilities ─────────────────────
        if agent_capabilities:
            karl = agent_capabilities.get("karl", False)
            if karl and confidence > 85 and signal == "NEUTRAL":
                # Grounding: high confidence + NEUTRAL = suspicious
                confidence = min(confidence, 75)
                logger.debug(f"[OutputAdapter] Grounding: NEUTRAL+high_conf → {confidence}")

        # ── Reasoning cleanup ───────────────────────────────────────────────
        if isinstance(reasoning, list):
            reasoning = "; ".join(str(r) for r in reasoning)
        reasoning = str(reasoning)[:2000]  # Truncate long reasoning

        return NormalizedOutput(
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            metadata=metadata,
            agent_name=agent_name,
            raw_output=data,
        )

    def adapt_many(
        self, outputs: List[Any], agent_names: List[str], capabilities: Optional[List[dict]] = None
    ) -> List[NormalizedOutput]:
        """Batch adapt — apply to list of (raw_output, agent_name)."""
        results = []
        caps = capabilities or [{}] * len(outputs)
        for raw, name, cap in zip(outputs, agent_names, caps):
            try:
                results.append(self.adapt(raw, name, cap))
            except Exception as e:
                logger.error(f"[OutputAdapter] Failed to adapt {name}: {e}")
                results.append(NormalizedOutput(
                    signal="NEUTRAL",
                    confidence=50,
                    reasoning=f"Adaptation error: {e}",
                    metadata={},
                    agent_name=name,
                    raw_output={},
                ))
        return results


# ─── Batch Analysis Helpers ──────────────────────────────────────────────────

def detect_disagreement(outputs: List[NormalizedOutput]) -> dict:
    """
    Detect conflicting signals across agents.
    Returns dict with disagreement metrics.
    """
    if not outputs:
        return {"disagreement": False, "bullish": 0, "bearish": 0, "neutral": 0}

    signals = [o.signal for o in outputs]
    bullish = sum(1 for s in signals if s == "BUY")
    bearish = sum(1 for s in signals if s == "SELL")
    neutral = sum(1 for s in signals if s in ("NEUTRAL", "AVOID"))
    total = len(signals)

    # Extreme disagreement: >1 bullish AND >1 bearish
    has_bull = bullish > 0
    has_bear = bearish > 0
    has_both = has_bull and has_bear

    # Strong disagreement: majority is NEUTRAL but extremes exist
    strong_disagreement = has_both and (bullish + bearish) >= total * 0.3

    return {
        "disagreement": has_both,
        "strong_disagreement": strong_disagreement,
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "bullish_pct": round(bullish / total * 100, 1) if total else 0,
        "bearish_pct": round(bearish / total * 100, 1) if total else 0,
        "consensus": "BULLISH" if bullish > bearish * 2 else "BEARISH" if bearish > bullish * 2 else "MIXED",
    }


def compute_weighted_signal(
    outputs: List[NormalizedOutput],
    weights: List[float],
    regime: str = "NORMAL",
    uncertainties: Optional[List[float]] = None,
) -> dict:
    """
    Compute regime-aware, uncertainty-weighted consensus signal.

    Formula:
        effective_confidence = confidence * (1 - uncertainty) * regime_multiplier
        weighted_score      = Σ(signal_value * effective_confidence * weight)
                               / Σ(weight * (1 - uncertainty))

    Prevents confidence inflation from:
      - high-confidence but uncertain agents dominating
      - HIGH/EXTREME regimes from giving false conviction
    """
    if not outputs or len(outputs) != len(weights):
        return {"weighted_score": 50, "final_signal": "NEUTRAL", "spread": 0,
                "effective_confidences": [], "regime_penalty": 0.0}

    # ── Regime multipliers ──────────────────────────────────────────────
    regime_multipliers = {"LOW": 1.0, "NORMAL": 1.0, "HIGH": 0.7, "EXTREME": 0.4}
    regime_mult = regime_multipliers.get(regime.upper(), 1.0)

    # ── Uncertainty ─────────────────────────────────────────────────────
    n = len(outputs)
    if uncertainties is None:
        uncertainties = [0.0] * n

    effective_confidences = []
    weighted_sum = 0.0
    weight_sum = 0.0
    confidences = []

    for out, w, unc in zip(outputs, weights, uncertainties):
        conf = out.confidence
        confidences.append(conf)

        # Signal value: BUY=+1, SELL=-1, NEUTRAL/AVOID=0
        if out.signal == "BUY":
            signal_value = 1.0
        elif out.signal == "SELL":
            signal_value = -1.0
        else:
            signal_value = 0.0

        # Effective confidence = confidence * uncertainty_discount * regime_mult
        uncertainty_discount = max(0.0, 1.0 - float(unc))
        eff_conf = conf * uncertainty_discount * regime_mult
        effective_confidences.append(eff_conf)

        # Weighted score contribution
        weighted_sum += signal_value * eff_conf * w
        # Weight denominator (discounted by uncertainty)
        weight_sum += w * uncertainty_discount

    # Weighted score normalized to [-100, +100]
    weighted_score = (weighted_sum / weight_sum * 100) if weight_sum else 0.0

    # ── Signal thresholds (regime-adjusted) ───────────────────────────────
    threshold_high = 15.0 / regime_mult   # harder to trigger in HIGH/EXTREME
    threshold_low  = -15.0 / regime_mult

    if weighted_score > threshold_high:
        final_signal = "BUY"
    elif weighted_score < threshold_low:
        final_signal = "SELL"
    else:
        final_signal = "NEUTRAL"

    avg_conf = sum(confidences) / len(confidences) if confidences else 50.0
    spread = max(confidences) - min(confidences) if confidences else 0.0
    avg_eff_conf = sum(effective_confidences) / len(effective_confidences) if effective_confidences else 0.0
    regime_penalty = (1.0 - regime_mult) * 100  # 0 for NORMAL, 30 for HIGH, 60 for EXTREME

    return {
        "weighted_score": round(weighted_score, 2),
        "final_signal": final_signal,
        "avg_confidence": round(avg_conf, 1),
        "avg_effective_confidence": round(avg_eff_conf, 1),
        "spread": round(spread, 1),
        "effective_confidences": [round(x, 1) for x in effective_confidences],
        "regime_penalty_pct": round(regime_penalty, 1),
        "regime_multiplier": regime_mult,
    }
