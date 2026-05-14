#!/usr/bin/env python3
"""GitAgent CLI — export-all + roundtrip + list. ATOM-GITAGENT-005."""
import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

LOG = Path(__file__).parent / "export.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# Static agent list (no exec side-effects)
AGENTS = [
    ("technical_agent", "TechnicalAgent", "technical", 0.10),
    ("sentiment_agent", "SentimentAgent", "sentiment", 0.10),
    ("options_flow_agent", "OptionsFlowAgent", "options", 0.15),
    ("market_analyst", "MarketAnalyst", "technical", 0.10),
    ("risk_agent", "RiskAgent", "risk", 0.05),
    ("bull_researcher", "BullResearcher", "bullish", 0.05),
    ("bear_researcher", "BearResearcher", "bearish", 0.05),
    ("electoral_agent", "ElectoralAgent", "electional", 0.03),
    ("bradley_agent", "BradleyAgent", "astro", 0.03),
    ("gann_agent", "GannAgent", "astro", 0.03),
    ("cycle_agent", "CycleAgent", "astro", 0.05),
    ("elliot_agent", "ElliotAgent", "technical", 0.05),
    ("time_window_agent", "TimeWindowAgent", "technical", 0.02),
    ("insider_agent", "InsiderAgent", "fundamental", 0.05),
    ("ml_predictor_agent", "MLPredictorAgent", "quant", 0.05),
    ("fundamental_agent", "FundamentalAgent", "fundamental", 0.20),
    ("quant_agent", "QuantAgent", "quant", 0.20),
    ("macro_agent", "MacroAgent", "macro", 0.15),
    ("astro_council", "AstroCouncil", "astro", 0.20),
    ("karl_synthesis", "KARLSynthesisAgent", "orchestrator", 0.00),
]


def export_all(args):
    t0 = time.time()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    agents = AGENTS
    if not args.include_karl:
        agents = [a for a in agents if a[0] != "karl_synthesis"]

    total = len(agents)
    ok = skip = err = 0
    errors = []

    print()
    print("=" * 60)
    print("  export-all — AstroFin Sentinel V5 GitAgent Export")
    print("=" * 60)
    print(f"  Output:  {out}")
    print(f"  Agents:  {total}")
    print(f"  Force:   {args.force}")
    print(f"  KARL:    {'yes' if args.include_karl else 'no'}")
    print("=" * 60)

    for i, (key, name, domain, weight) in enumerate(agents, 1):
        pkg = out / key
        try:
            pkg.mkdir(parents=True, exist_ok=True)
            # Write agent.yaml
            yaml_content = f"""name: "{name}"
description: "GitAgent package for {name} — AstroFin Sentinel V5"
version: "5.0"
domain: {domain}
weight: {weight}
karl_integrated: true
output_schema:
  signal: LONG | SHORT | NEUTRAL | BUY | SELL | AVOID
  confidence: 0-100
  reasoning: string
  sources: list
  metadata: dict
"""
            (pkg / "agent.yaml").write_text(yaml_content)
            # Write SOUL.md
            soul = f"""# {name} — SOUL

## Identity
You are **{name}**, a specialized financial analysis agent in AstroFin Sentinel V5.

## KARL Integration
- All decisions generate DecisionRecords for audit trail
- Uncertainty quantified before reporting confidence
- AMRE validation applies to all outputs
- Self-questioning on high-disagreement states
"""
            (pkg / "SOUL.md").write_text(soul)
            # Write RULES.md
            rules = f"""# {name} — RULES

## Absolute Rules (Never Violate)
1. Quantify uncertainty before confidence
2. Generate DecisionRecord per decision
3. Apply volatility regime guards
4. Use grounding validation
5. Never report confidence > 95%
6. Acknowledge astro/fundamental conflicts
7. Use EMA-smoothed reward
"""
            (pkg / "RULES.md").write_text(rules)
            # Write DUTIES.md
            duties = f"""# {name} — DUTIES

## Responsibilities
- Analyze {domain} signals
- Generate recommendations with confidence
- Log decisions for KARL audit

## Output
signal, confidence, reasoning, sources, metadata
"""
            (pkg / "DUTIES.md").write_text(duties)

            n_files = len(list(pkg.iterdir()))
            print(f"  [{i:2d}/{total}] OK  {key} ({n_files} files)")
            ok += 1
        except Exception as e:
            print(f"  [{i:2d}/{total}] FAIL {key}: {e}")
            err += 1
            errors.append(f"{key}: {e}")
        log.info(f"export {key}")

    elapsed = time.time() - t0
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) // 1024

    print()
    print("=" * 60)
    print(f"  Results: {ok} exported, {skip} skipped, {err} errors")
    print(f"  Time:    {elapsed:.1f}s")
    print(f"  Size:    {size}KB")
    print("=" * 60)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    log.info(f"export-all complete: {ok} ok, {skip} skip, {err} err, {elapsed:.1f}s")
    return 0 if err == 0 else 1


def roundtrip(args):
    out = Path(args.output_dir)
    SKIP_DIRS = {"__pycache__", "adapters", "docs", "__init__", "test", "tests"}
    dirs = sorted([d for d in out.iterdir() if d.is_dir() and d.name not in SKIP_DIRS])
    ok = fail = 0
    print()
    print("=" * 60)
    print("  Round-trip Validation")
    print("=" * 60)
    for d in dirs:
        yaml_file = d / "agent.yaml"
        if yaml_file.exists():
            try:
                data = yaml.safe_load(yaml_file.read_text())
                has_soul = (d / "SOUL.md").exists()
                has_rules = (d / "RULES.md").exists()
                has_duties = (d / "DUTIES.md").exists()
                status = "OK" if all([has_soul, has_rules, has_duties]) else "WARN"
                if status == "OK":
                    ok += 1
                else:
                    fail += 1
                print(f"  {status} {d.name}")
            except Exception:
                fail += 1
                print(f"  FAIL {d.name} (yaml error)")
        else:
            fail += 1
            print(f"  FAIL {d.name} (no agent.yaml)")
    total = ok + fail
    print()
    print("=" * 60)
    fail_str = f", {fail} failed" if fail else ""
    print(f"  Round-trip: {ok}/{total} passed{fail_str}")
    print("=" * 60)
    return 0 if fail == 0 else 1


def cmd_list(args):
    for key, name, domain, weight in AGENTS:
        print(f"  {key}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="GitAgent CLI — AstroFin Sentinel V5")
    sub = p.add_subparsers(dest="cmd")

    ea = sub.add_parser("export-all", help="Export ALL agents")
    ea.add_argument("--output-dir", default="integrations/gitagent")
    ea.add_argument("--force", action="store_true")
    ea.add_argument("--include-karl", action="store_true")
    ea.set_defaults(func=export_all)

    rt = sub.add_parser("roundtrip", help="Validate all packages")
    rt.add_argument("--output-dir", default="integrations/gitagent")
    rt.set_defaults(func=roundtrip)

    li = sub.add_parser("list", help="List all agents")
    li.set_defaults(func=cmd_list)

    if len(sys.argv) == 1:
        p.print_help()
        print()
        print("Commands:")
        print("  python -m integrations.gitagent.cli export-all [--flags]")
        print("  python -m integrations.gitagent.cli roundtrip [--output-dir]")
        print("  python -m integrations.gitagent.cli list")
    else:
        args = p.parse_args()
        sys.exit(args.func(args) if hasattr(args, "func") else 0)
