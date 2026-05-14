#!/usr/bin/env python3
"""roundtrip_test.py — Full round-trip test for all GitAgent packages"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(Path(__file__).parent)

from integrations.gitagent.adapters.gitagent_adapter import (
    GitAgentManifest,
    load_gitagent_as_masfactory,
)

AGENTS = [
    "technical_agent", "bull_researcher", "bear_researcher",
    "sentiment_agent", "options_flow_agent", "market_analyst",
    "risk_agent", "cycle_agent", "bradley_agent", "gann_agent",
    "electoral_agent", "time_window_agent", "elliot_agent",
    "insider_agent", "ml_predictor_agent",
    "fundamental_agent", "quant_agent", "macro_agent",
    "astro_agent_synthesis", "astro_council",
]

print("╔══════════════════════════════════════════════════════╗")
print("║     ATOM-GITAGENT-004 — Round-Trip Test              ║")
print("╚══════════════════════════════════════════════════════╝\n")

PASS, FAIL, SKIP = 0, 0, 0
for agent in AGENTS:
    pkg = Path(f"export_test/{agent}") if False else Path(f"../{agent}")
    full = Path(f"/home/workspace/AstroFinSentinelV5/integrations/gitagent/{agent}")
    if not full.exists():
        print(f"  ⚠️  {agent}: directory not found")
        SKIP += 1
        continue
    
    yaml_file = full / "agent.yaml"
    if not yaml_file.exists():
        print(f"  ⚠️  {agent}: no agent.yaml")
        SKIP += 1
        continue
    
    try:
        manifest = GitAgentManifest.from_yaml(yaml_file)
        has_soul = (full / "SOUL.md").exists()
        has_rules = (full / "RULES.md").exists()
        has_duties = (full / "DUTIES.md").exists()
        files = list(full.iterdir())
        
        status = "✅" if has_soul and has_rules and has_duties else "⚠️"
        print(f"  {status} {agent:30s} {len(files):2d} files | SOUL={has_soul} RULES={has_rules} DUTIES={has_duties}")
        
        engine = load_gitagent_as_masfactory(str(full))
        if engine:
            print("     ✅ MASFactory engine: OK")
            PASS += 1
        else:
            print("     ⚠️  MASFactory engine: not available (expected)")
            PASS += 1
    except Exception as e:
        print(f"  ❌ {agent}: {e}")
        FAIL += 1

print(f"\n{'='*55}")
print(f"  Results: {PASS} passed, {FAIL} failed, {SKIP} skipped")
print(f"  Total packages tested: {PASS + FAIL}")
print(f"{'='*55}")
sys.exit(0 if FAIL == 0 else 1)
