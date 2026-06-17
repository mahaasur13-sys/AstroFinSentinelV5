#!/usr/bin/env python3
"""
Validate that all alert rules reference metrics defined in meta_rl/metrics.py.
Parses meta_rl/metrics.py to extract the canonical metric name set, then
cross-checks against deploy/monitoring/alerts.yml.
"""
import re
import sys
from pathlib import Path

import yaml


def _canonical_metrics(metrics_path: Path) -> set[str]:
    text = metrics_path.read_text()
    pattern = re.compile(
        r'(?:Counter|Gauge|Histogram|Summary)\(\s*[\'"]([a-zA-Z_:][a-zA-Z0-9_:]*)[\'"]'
    )
    names = set(pattern.findall(text))
    names = {n.removesuffix("_total") for n in names}
    return names


def _alerts_metrics(alerts_path: Path) -> set[str]:
    data = yaml.safe_load(alerts_path.read_text())
    out: set[str] = set()
    for group in data.get("groups", []):
        for rule in group.get("rules", []):
            expr = rule.get("expr", "")
            for token in re.findall(r"\b([a-zA-Z_:][a-zA-Z0-9_:]*)\b", expr):
                if token.isupper():
                    continue
                if token in {
                    "rate", "irate", "increase", "sum", "avg", "max", "min",
                    "by", "without", "offset", "on", "ignoring",
                    "group_left", "group_right", "bool", "time",
                    "abs", "ceil", "floor", "round", "ln", "log2", "log10",
                    "exp", "sqrt", "pow", "clamp", "clamp_min", "clamp_max",
                    "sgn", "histogram_quantile", "deriv", "predict_linear",
                    "topk", "bottomk", "quantile", "stddev", "stdvar",
                    "count", "count_values", "absent", "present_over_time",
                }:
                    continue
                out.add(token)
    return out


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    metrics_path = root / "meta_rl" / "metrics.py"
    alerts_path = root / "deploy" / "monitoring" / "alerts.yml"

    if not metrics_path.exists():
        print(f"ERROR: {metrics_path} not found")
        return 1
    if not alerts_path.exists():
        print(f"ERROR: {alerts_path} not found")
        return 1

    canonical = _canonical_metrics(metrics_path)
    referenced = _alerts_metrics(alerts_path)
    missing = referenced - canonical

    if missing:
        print("ERROR: Alert rules reference metrics not defined in meta_rl/metrics.py:")
        for m in sorted(missing):
            print(f"  - {m}")
        print(f"\nAdd Gauge/Counter/Histogram entries to meta_rl/metrics.py for these names.")
        return 1

    print(f"OK: All {len(referenced)} alert metrics are defined in meta_rl/metrics.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
