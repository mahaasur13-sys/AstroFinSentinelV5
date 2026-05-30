"""migrate_agents.py — ATOM-VALIDATE-001: Bulk migration of agent.yaml to schema v1.1"""

import re
from pathlib import Path
from typing import Any, Dict

import yaml

BASE_DIR = Path("/home/workspace/AstroFinSentinelV5/integrations/gitagent")

# Domain → capabilities/tools/rules inference
DOMAIN_DEFAULTS = {
    "astro": {
        "capabilities": [
            "planetary_analysis",
            "aspect_calculation",
            "ephemeris_lookup",
        ],
        "tools": ["swiss_ephemeris", "natal_chart", "transit_calc"],
        "rules": [
            "Use Swiss Ephemeris for all planetary calculations",
            "Apply orbs from configuration",
        ],
    },
    "fundamental": {
        "capabilities": ["fundamental_analysis", "valuation", "financial_metrics"],
        "tools": ["coingecko_api", "sec_filings", "financial_indicators"],
        "rules": [
            "Always cite sources for financial data",
            "Cross-reference multiple data sources",
        ],
    },
    "quant": {
        "capabilities": [
            "quantitative_analysis",
            "ml_prediction",
            "statistical_modeling",
        ],
        "tools": ["backtest_engine", "ml_predictor", "statistical_analysis"],
        "rules": [
            "Use walk-forward validation",
            "Report uncertainty with every prediction",
        ],
    },
    "macro": {
        "capabilities": [
            "macro_analysis",
            "economic_indicators",
            "market_regime_detection",
        ],
        "tools": ["economic_data", "vix_monitor", "dxy_tracker"],
        "rules": [
            "Monitor VIX and DXY for regime changes",
            "Apply volatility-adjusted position sizing",
        ],
    },
    "technical": {
        "capabilities": [
            "technical_analysis",
            "pattern_recognition",
            "indicator_calculation",
        ],
        "tools": ["price_chart", "rsi", "macd", "bollinger_bands"],
        "rules": [
            "Use multiple timeframes for confirmation",
            "Apply volatility filters",
        ],
    },
    "options": {
        "capabilities": [
            "options_flow_analysis",
            "gamma_exposure",
            "unusual_activity_detection",
        ],
        "tools": ["options_scanner", "gamma_analysis", "flow_monitor"],
        "rules": ["Flag unusual options activity above 1.5x average"],
    },
    "sentiment": {
        "capabilities": ["sentiment_analysis", "social_monitoring", "news_analysis"],
        "tools": ["news_feed", "social_sentiment", "fear_greed_index"],
        "rules": [
            "Aggregate sentiment across multiple sources",
            "Apply time-decay to news",
        ],
    },
    "risk": {
        "capabilities": ["risk_assessment", "portfolio_risk", "drawdown_tracking"],
        "tools": ["risk_calculator", "var_computation", "stress_testing"],
        "rules": [
            "Always apply volatility-adjusted sizing",
            "Cap maximum drawdown exposure",
        ],
    },
    "electional": {
        "capabilities": [
            "electional_astrology",
            "muhurta_timing",
            "choghadiya_analysis",
        ],
        "tools": ["choghadiya_table", "nakshatra_calc", "panchanga"],
        "rules": ["Prefer auspicious Yoga for entries", "Avoid malefic windows"],
    },
    "orchestrator": {
        "capabilities": ["orchestration", "agent_coordination", "synthesis"],
        "tools": ["agent_dispatcher", "result_aggregator"],
        "rules": [
            "Coordinate all sub-agents before synthesis",
            "Apply weighted aggregation",
        ],
    },
}

DEFAULT_MODEL = {"provider": "openai", "name": "gpt-4o-mini", "temperature": 0.3}


def infer_domain(name: str, data: Dict[str, Any]) -> str:
    if "domain" in data and data["domain"]:
        return data["domain"]
    name_lower = name.lower()
    for domain in DOMAIN_DEFAULTS:
        if domain in name_lower:
            return domain
    return "fundamental"


def infer_name(name_raw: Any) -> str:
    """Normalize name: strip quotes, lowercase, snake_case."""
    if not isinstance(name_raw, str):
        name_raw = str(name_raw)
    # Strip surrounding quotes if quoted
    name_raw = name_raw.strip('"').strip("'")
    # Lowercase
    name = name_raw.lower()
    # Replace uppercase runs (like "MacroAgent") with snake_case
    # e.g. "MacroAgent" → "macro_agent", "MLPredictorAgent" → "ml_predictor_agent"
    name = re.sub(
        r"([A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+)", lambda m: m.group(1).lower(), name
    )
    name = re.sub(r"([A-Z]+)", lambda m: "_" + m.group(1).lower(), name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def fix_sources(oschema: Any) -> Any:
    """Fix sources: 'list' string → [], preserve array."""
    if isinstance(oschema, dict) and "sources" in oschema:
        if oschema["sources"] == "list":
            oschema["sources"] = []
        elif isinstance(oschema["sources"], list):
            pass  # already correct
    return oschema


def migrate_agent(yaml_path: Path) -> Dict[str, Any]:
    """Load, migrate, and return agent data dict."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    original = dict(data)

    # 1. Normalize name
    raw_name = data.get("name", yaml_path.parent.name)
    normalized_name = infer_name(raw_name)
    data["name"] = normalized_name

    # 2. Fix sources: list → []
    if "output_schema" in data:
        fix_sources(data["output_schema"])

    # 3. Ensure version is clean string
    if "version" in data:
        data["version"] = str(data["version"]).lstrip("v")

    # 4. Domain
    domain = infer_domain(normalized_name, data)
    data["domain"] = domain

    # 5. Inject missing required fields
    domain_defaults = DOMAIN_DEFAULTS.get(domain, DOMAIN_DEFAULTS["fundamental"])

    if "model" not in data or not data["model"]:
        data["model"] = dict(DEFAULT_MODEL)

    if "capabilities" not in data or not data["capabilities"]:
        # Try to extract from DUTIES.md
        duties_path = yaml_path.parent / "DUTIES.md"
        if duties_path.exists():
            content = duties_path.read_text()
            caps = re.findall(r"##?\s*(\w[\w\s]*?)(?:\n|$)", content[:500])
            if caps:
                data["capabilities"] = [
                    c.strip().lower().replace(" ", "_")
                    for c in caps[:5]
                    if len(c.strip()) > 3
                ]
        if not data.get("capabilities"):
            data["capabilities"] = domain_defaults["capabilities"]

    if "tools" not in data or not data["tools"]:
        data["tools"] = domain_defaults["tools"]

    if "rules" not in data or not data["rules"]:
        # Try to extract from RULES.md
        rules_path = yaml_path.parent / "RULES.md"
        if rules_path.exists():
            content = rules_path.read_text()
            rules = re.findall(r"[-*]?\s*(.+?)(?:\n|$)", content[:800])
            if rules:
                data["rules"] = [r.strip() for r in rules if len(r.strip()) > 10][:5]
        if not data.get("rules"):
            data["rules"] = domain_defaults["rules"]

    # 6. Ensure output_schema exists with minimum fields
    if "output_schema" not in data or not data["output_schema"]:
        data["output_schema"] = {
            "signal": "LONG | SHORT | NEEUTRAL | BUY | SELL | AVOID",
            "confidence": "0-100",
            "reasoning": "string",
            "sources": [],
        }
    else:
        oschema = data["output_schema"]
        if "signal" not in oschema:
            oschema["signal"] = "LONG | SHORT | NEUTRAL | BUY | SELL | AVOID"
        if "confidence" not in oschema:
            oschema["confidence"] = "0-100"
        if "reasoning" not in oschema:
            oschema["reasoning"] = "string"
        fix_sources(oschema)

    return data, original


def migrate_all():
    """Migrate all agent.yaml files in integrations/gitagent/."""
    agent_dirs = [
        d for d in BASE_DIR.iterdir() if d.is_dir() and (d / "agent.yaml").exists()
    ]
    agent_dirs.sort()

    results = []
    for agent_dir in agent_dirs:
        yaml_path = agent_dir / "agent.yaml"
        try:
            migrated, original = migrate_agent(yaml_path)

            # Write back
            with open(yaml_path, "w") as f:
                yaml.dump(migrated, f, sort_keys=False, allow_unicode=True, width=120)

            changes = []
            if original.get("name") != migrated["name"]:
                changes.append(f"name: {original.get('name')!r} → {migrated['name']!r}")
            if original.get("output_schema", {}).get("sources") == "list":
                changes.append("sources: 'list' → []")
            if "model" not in original:
                changes.append("+model")
            if "capabilities" not in original:
                changes.append("+capabilities")
            if "tools" not in original:
                changes.append("+tools")
            if "rules" not in original:
                changes.append("+rules")
            if "output_schema" not in original:
                changes.append("+output_schema")

            results.append(
                {
                    "name": migrated["name"],
                    "path": str(yaml_path.relative_to(BASE_DIR.parent.parent.parent)),
                    "status": "migrated",
                    "changes": changes,
                }
            )
        except Exception as e:
            results.append(
                {
                    "name": agent_dir.name,
                    "path": str(yaml_path),
                    "status": f"ERROR: {e}",
                    "changes": [],
                }
            )

    return results


if __name__ == "__main__":
    print("\nATOM-VALIDATE-001: Bulk Agent Migration")
    print("=" * 60)
    results = migrate_all()

    for r in results:
        status_icon = "✅" if r["status"] == "migrated" else "❌"
        print(f"\n{status_icon} {r['name']}")
        for ch in r["changes"]:
            print(f"   • {ch}")

    passed = sum(1 for r in results if r["status"] == "migrated")
    failed = sum(1 for r in results if r["status"] != "migrated")
    print(f"\n{'=' * 60}")
    print(f"Migrated: {passed}/{len(results)}")
    if failed:
        print(f"Failed: {failed}")
    print()
