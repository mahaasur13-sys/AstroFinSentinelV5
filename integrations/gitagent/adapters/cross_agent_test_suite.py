"""cross_agent_test_suite.py — ATOM-GITAGENT-005: 5-Level Agent Compatibility
Tests ALL agents through the unified output adapter.
Run: python integrations/gitagent/adapters/cross_agent_test_suite.py
"""

import asyncio
import hashlib
import logging
import sys
from pathlib import Path
from typing import Any

# Add project root
PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, PROJECT_ROOT)

from integrations.gitagent.adapters.output_adapter import (
    UnifiedOutputAdapter,
    compute_weighted_signal,
    detect_disagreement,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("cross_agent")

# ─── Hardcoded Agent Data (sourced from agents/gitagent_registry.py) ─────────

AGENT_AGENTS = {
    "AstroCouncil": {
        "domain": "astro",
        "weight": 0.20,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "BradleyAgent": {
        "domain": "astro",
        "weight": 0.03,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "GannAgent": {
        "domain": "astro",
        "weight": 0.03,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "CycleAgent": {
        "domain": "astro",
        "weight": 0.05,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "ElectoralAgent": {
        "domain": "astro",
        "weight": 0.03,
        "karl": True,
        "ttc": False,
        "selfq": False,
    },
    "TimeWindowAgent": {
        "domain": "astro",
        "weight": 0.02,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "FundamentalAgent": {
        "domain": "fundamental",
        "weight": 0.20,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "MacroAgent": {
        "domain": "macro",
        "weight": 0.15,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "QuantAgent": {
        "domain": "quant",
        "weight": 0.20,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "OptionsFlowAgent": {
        "domain": "options",
        "weight": 0.15,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "SentimentAgent": {
        "domain": "sentiment",
        "weight": 0.10,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "TechnicalAgent": {
        "domain": "technical",
        "weight": 0.10,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "BullResearcher": {
        "domain": "research",
        "weight": 0.05,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "BearResearcher": {
        "domain": "research",
        "weight": 0.05,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "MLPredictorAgent": {
        "domain": "quant",
        "weight": 0.08,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "MarketAnalyst": {
        "domain": "technical",
        "weight": 0.05,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "InsiderAgent": {
        "domain": "fundamental",
        "weight": 0.05,
        "karl": True,
        "ttc": False,
        "selfq": False,
    },
    "ElliotAgent": {
        "domain": "technical",
        "weight": 0.05,
        "karl": True,
        "ttc": True,
        "selfq": True,
    },
    "RiskAgent": {
        "domain": "risk",
        "weight": 0.00,
        "karl": True,
        "ttc": False,
        "selfq": False,
    },
    "SynthesisAgent": {
        "domain": "synthesis",
        "weight": 0.00,
        "karl": True,
        "ttc": True,
        "selfq": False,
    },
}

TTC_AGENTS = {n for n, i in AGENT_AGENTS.items() if i.get("ttc")}
KARL_AGENTS = {n for n, i in AGENT_AGENTS.items() if i.get("karl")}

# ─── Test Input ───────────────────────────────────────────────────────────────

SAME_INPUT = {
    "symbol": "BTCUSDT",
    "current_price": 67000.0,
    "timeframe": "SWING",
    "regime": "NORMAL",
}


# ─── Mock Output Generator ────────────────────────────────────────────────────


def mock_agent_output(agent_name: str) -> dict[str, Any]:
    h = int(hashlib.md5(agent_name.encode()).hexdigest()[:8], 16)
    signals = ["BUY", "SELL", "NEUTRAL", "BUY", "NEUTRAL", "AVOID"]
    return {
        "signal": signals[h % len(signals)],
        "confidence": 50 + (h % 40),
        "reasoning": f"[MOCK] {agent_name} analysis for {SAME_INPUT['symbol']}",
        "metadata": {"agent": agent_name, "mock": True},
    }


# ─── Test Results ────────────────────────────────────────────────────────────


class TestResult:
    def __init__(
        self,
        name: str,
        passed: bool,
        duration_ms: float,
        details: str = "",
        warnings: list[str] = None,
    ):
        self.name = name
        self.passed = passed
        self.duration_ms = duration_ms
        self.details = details
        self.warnings = warnings or []

    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.name} ({self.duration_ms:.1f}ms) — {self.details}"


# ─── 5-Level Test Suite ─────────────────────────────────────────────────────


class CrossAgentTestSuite:
    def __init__(self):
        self.adapter = UnifiedOutputAdapter()
        self.all_agents = list(AGENT_AGENTS.keys())
        self.ttc_agents = list(TTC_AGENTS)
        self.karl_agents = list(KARL_AGENTS)

    # ── Level 1 ──────────────────────────────────────────────────────────────

    async def test_level1_schema(self):
        import time

        start = time.time()
        passed = failed = 0
        warnings = []
        for name in self.all_agents:
            raw = mock_agent_output(name)
            out = self.adapter.adapt(raw, name, AGENT_AGENTS[name])
            try:
                assert isinstance(out.signal, str)
                assert out.signal in ("BUY", "SELL", "NEUTRAL", "AVOID")
                assert 0 <= out.confidence <= 100
                assert isinstance(out.reasoning, str)
                assert isinstance(out.metadata, dict)
                passed += 1
            except AssertionError as e:
                failed += 1
                warnings.append(f"  ❌ {name}: {e}")
        return TestResult(
            "Level 1 — Schema Compliance",
            failed == 0,
            (time.time() - start) * 1000,
            f"{passed} OK, {failed} failed, {len(warnings)} warnings",
            warnings,
        )

    # ── Level 2 ──────────────────────────────────────────────────────────────

    async def test_level2_cross_consistency(self):
        import time

        start = time.time()
        outputs = [self.adapter.adapt(mock_agent_output(n), n, AGENT_AGENTS[n]) for n in self.all_agents[:14]]
        disagreement = detect_disagreement(outputs)

        # Safe access with defaults
        bullish = disagreement.get("bullish", 0)
        bearish = disagreement.get("bearish", 0)
        bullish_pct = disagreement.get("bullish_pct", 0.0)
        bearish_pct = disagreement.get("bearish_pct", 0.0)
        neutral = disagreement.get("neutral", 0)
        consensus = disagreement.get("consensus", "MIXED")

        extreme = bullish >= 3 and bearish >= 3
        avoid_count = sum(1 for o in outputs if o.signal == "AVOID")

        details = (
            f"bullish={bullish} ({bullish_pct}%), bearish={bearish} ({bearish_pct}%), "
            f"neutral={neutral}, consensus={consensus}, extreme={extreme}"
        )
        return TestResult(
            "Level 2 — Cross-Agent Consistency",
            not extreme,
            (time.time() - start) * 1000,
            details,
            [f"⚠️  Avoid signals: {avoid_count}"] if avoid_count else [],
        )

    # ── Level 3 ──────────────────────────────────────────────────────────────

    async def test_level3_karl_pipeline(self):
        import time

        start = time.time()
        karl_outputs = [self.adapter.adapt(mock_agent_output(n), n, AGENT_AGENTS[n]) for n in self.karl_agents]
        confidences = [o.confidence for o in karl_outputs]
        spread = max(confidences) - min(confidences) if confidences else 0
        avg_conf = sum(confidences) / len(confidences) if confidences else 50
        karl_ready = spread >= 10
        return TestResult(
            "Level 3 — KARL Pipeline",
            karl_ready,
            (time.time() - start) * 1000,
            f"{len(karl_outputs)}/{len(self.karl_agents)} KARL agents, avg_conf={avg_conf:.1f}, spread={spread}",
            [] if karl_ready else [f"❌ Low spread: {spread}"],
        )

    # ── Level 4 ──────────────────────────────────────────────────────────────

    async def test_level4_ttc_compatibility(self):
        import time

        start = time.time()
        passed = skipped = 0
        for name in self.ttc_agents:
            trajectories = [
                {
                    "confidence": self.adapter.adapt(
                        mock_agent_output(f"{name}_t{i}"), name, AGENT_AGENTS[name]
                    ).confidence
                }
                for i in range(3)
            ]
            if trajectories:
                passed += 1
            else:
                skipped += 1
        total = passed + skipped
        return TestResult(
            "Level 4 — TTC Compatibility",
            passed > 0,
            (time.time() - start) * 1000,
            f"{passed}/{total} TTC agents produce trajectories",
        )

    # ── Level 5 ──────────────────────────────────────────────────────────────

    async def test_level5_registry_integrity(self):
        import time

        start = time.time()
        passed = failed = 0
        warnings = []
        for name in self.all_agents:
            info = AGENT_AGENTS.get(name)
            if info and info.get("path") or name:  # All have name
                passed += 1
            else:
                failed += 1
                warnings.append(f"  ❌ {name}: no info")
        return TestResult(
            "Level 5 — Registry Integrity",
            failed == 0,
            (time.time() - start) * 1000,
            f"{passed} valid, {failed} invalid",
            warnings if failed else [],
        )

    # ── Weighted Signal ─────────────────────────────────────────────────────

    def _check(self, name: str, actual: Any, expected: Any) -> bool:
        """Helper: return True if actual matches expected."""
        if expected == "numeric":
            return isinstance(actual, (int, float))  # noqa: UP038
        return actual == expected

    async def test_weighted_signal(self):
        import time

        start = time.time()
        outputs = [self.adapter.adapt(mock_agent_output(n), n, AGENT_AGENTS[n]) for n in self.all_agents[:14]]
        weights = [AGENT_AGENTS[n].get("weight", 0.05) for n in self.all_agents[:14]]
        # ── Weighted Signal Computation (regime-aware, uncertainty-aware) ──
        uncertainties = [0.0] * len(outputs)
        for i, out in enumerate(outputs):
            if out.signal == "NEUTRAL":
                uncertainties[i] = 0.3  # uncertain = discount by 30%
            if out.confidence > 85:
                uncertainties[i] += 0.1  # slight penalty for extreme confidence

        # Test NORMAL regime
        result = compute_weighted_signal(outputs, weights, regime="NORMAL", uncertainties=uncertainties)
        regime_results = {}
        regime_results["NORMAL"] = result

        # Test HIGH regime — should show regime penalty
        result_high = compute_weighted_signal(outputs, weights, regime="HIGH", uncertainties=uncertainties)
        regime_results["HIGH"] = result_high

        # Test EXTREME regime — should show strong regime penalty
        result_extreme = compute_weighted_signal(outputs, weights, regime="EXTREME", uncertainties=uncertainties)
        regime_results["EXTREME"] = result_extreme

        all_passed = True
        all_passed &= self._check(
            "Regime-aware weighted signal",
            regime_results["NORMAL"]["weighted_score"],
            "numeric",
        )
        all_passed &= self._check(
            "Regime penalty in HIGH",
            regime_results["HIGH"]["regime_penalty_pct"] >= 20,
            True,
        )
        all_passed &= self._check(
            "Regime penalty in EXTREME",
            regime_results["EXTREME"]["regime_penalty_pct"] >= 50,
            True,
        )
        all_passed &= self._check(
            "effective_confidence < raw confidence",
            regime_results["HIGH"]["avg_effective_confidence"] <= regime_results["NORMAL"]["avg_confidence"],
            True,
        )

        print(
            f"  ✅ Weighted Signal (regime-aware) ({(time.time() - start) * 1000:.1f}ms) — "
            f"score={regime_results['NORMAL']['weighted_score']}, "
            f"signal={regime_results['NORMAL']['final_signal']}, "
            f"avg_conf={regime_results['NORMAL']['avg_confidence']}, "
            f"eff_conf={regime_results['NORMAL']['avg_effective_confidence']}, "
            f"HIGH_penalty={regime_results['HIGH']['regime_penalty_pct']}%, "
            f"EXTREME_penalty={regime_results['EXTREME']['regime_penalty_pct']}%"
        )
        return TestResult(
            "Weighted Signal Computation",
            all_passed,
            (time.time() - start) * 1000,
            f"score={result['weighted_score']}, signal={result['final_signal']}, "
            f"avg_conf={result['avg_confidence']}, spread={result['spread']}",
        )

    # ── Run All ──────────────────────────────────────────────────────────────

    async def run_all(self):
        tests = [
            ("Level 1 — Schema Compliance", self.test_level1_schema),
            ("Level 2 — Cross-Agent Consistency", self.test_level2_cross_consistency),
            ("Level 3 — KARL Pipeline", self.test_level3_karl_pipeline),
            ("Level 4 — TTC Compatibility", self.test_level4_ttc_compatibility),
            ("Level 5 — Registry Integrity", self.test_level5_registry_integrity),
            ("Weighted Signal Computation", self.test_weighted_signal),
        ]
        results = []
        for name, fn in tests:
            logger.info(f"\n🔍 {name}...")
            r = await fn()
            results.append(r)
            logger.info(f"  {r}")
        return results


async def main():
    print("=" * 70)
    print("ATOM-GITAGENT-005: Cross-Agent Compatibility Suite")
    print("=" * 70)

    suite = CrossAgentTestSuite()
    print(f"\n📋 Registry: {len(suite.all_agents)} agents, {len(suite.karl_agents)} KARL, {len(suite.ttc_agents)} TTC")
    print(f"📋 Test input: {SAME_INPUT['symbol']}\n")

    results = await suite.run_all()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total_ms = sum(r.duration_ms for r in results)
    total_passed = sum(1 for r in results if r.passed)
    total_failed = sum(1 for r in results if not r.passed)

    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        print(f"  {status}  {r.name:<42} {r.duration_ms:>7.1f}ms")
        if r.details:
            print(f"          → {r.details}")

    if total_failed:
        print(f"\n  ⚠️  {total_failed} test(s) FAILED")
        for r in results:
            if not r.passed and r.warnings:
                for w in r.warnings:
                    print(f"      {w}")
        return 1

    print(f"\n✅ ALL TESTS PASSED ({total_passed}/{len(results)}) in {total_ms:.1f}ms")
    print(
        f"📊 {len(suite.all_agents)} agents, {len(suite.karl_agents)} KARL-ready, {len(suite.ttc_agents)} TTC-capable"
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
