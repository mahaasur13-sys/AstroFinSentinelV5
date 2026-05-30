"""agent_validator.py — ATOM-VALIDATE-001: JSON Schema validator for agent.yaml"""

import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

try:
    import jsonschema

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

# ─── Types ───────────────────────────────────────────────────────────────────────


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    path: str
    value: Any
    expected: str
    severity: Severity
    message: str


@dataclass
class ValidationResult:
    agent_name: str
    file_path: Path
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    infos: list[ValidationIssue] = field(default_factory=list)


@dataclass
class ValidationReport:
    total: int = 0
    passed: int = 0
    failed: int = 0
    warning_count: int = 0
    results: list[ValidationResult] = field(default_factory=list)


# ─── Colors ──────────────────────────────────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


# ─── AgentYamlValidator ──────────────────────────────────────────────────────────


class AgentYamlValidator:
    """Validates agent.yaml files against JSON Schema."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path or self._find_schema()
        self.schema = self._load_schema()
        self.checked_dirs: set = set()

    def _find_schema(self) -> Path:
        p = Path(__file__).parent.parent / "schema" / "agent.schema.json"
        if p.exists():
            return p
        # Try relative to project root
        p2 = Path("integrations/gitagent/schema/agent.schema.json")
        if p2.exists():
            return p2
        raise FileNotFoundError(f"Schema not found at {p}")

    def _load_schema(self) -> dict:
        with open(self.schema_path) as f:
            return json.load(f)

    def validate_file(self, yaml_path: Path) -> ValidationResult:
        """Validate a single agent.yaml file."""
        result = ValidationResult(
            agent_name=yaml_path.parent.name,
            file_path=yaml_path,
            valid=True,
        )

        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.valid = False
            result.errors.append(
                ValidationIssue(
                    path="<file>",
                    value=str(e)[:100],
                    expected="valid YAML",
                    severity=Severity.ERROR,
                    message=f"YAML parse error: {e}",
                )
            )
            return result

        if not isinstance(data, dict):
            result.valid = False
            result.errors.append(
                ValidationIssue(
                    path="<root>",
                    value=type(data).__name__,
                    expected="object",
                    severity=Severity.ERROR,
                    message="Root must be an object",
                )
            )
            return result

        # ── Required fields ──────────────────────────────────────────────────
        required_fields = [
            "name",
            "description",
            "version",
            "model",
            "capabilities",
            "tools",
            "rules",
            "output_schema",
        ]
        for field_name in required_fields:
            if field_name not in data:
                result.valid = False
                result.errors.append(
                    ValidationIssue(
                        path=field_name,
                        value=None,
                        expected="present",
                        severity=Severity.ERROR,
                        message=f"Required field '{field_name}' is missing",
                    )
                )

        # ── name pattern ─────────────────────────────────────────────────────
        if "name" in data:
            import re

            if not re.match(r"^[a-z0-9_\-]+$", data["name"]):
                result.errors.append(
                    ValidationIssue(
                        path="name",
                        value=data["name"],
                        expected="lowercase with hyphens/underscores only",
                        severity=Severity.ERROR,
                        message=f"Invalid name '{data['name']}': must match ^[a-z0-9_\\-]+$",
                    )
                )
                result.valid = False

        # ── description length ────────────────────────────────────────────────
        if "description" in data:
            if len(data["description"]) < 10:
                result.warnings.append(
                    ValidationIssue(
                        path="description",
                        value=f"length={len(data['description'])}",
                        expected="minLength=10",
                        severity=Severity.WARNING,
                        message=f"Description too short ({len(data['description'])} chars)",
                    )
                )

        # ── version pattern ───────────────────────────────────────────────────
        if "version" in data:
            import re

            if not re.match(r"^\d+\.\d+(\.\d+)?$", data["version"]):
                result.errors.append(
                    ValidationIssue(
                        path="version",
                        value=data["version"],
                        expected="MAJOR.MINOR or MAJOR.MINOR.PATCH",
                        severity=Severity.ERROR,
                        message=f"Invalid version '{data['version']}': must match ^\\d+\\.\\d+(\\.\\d+)?$",
                    )
                )
                result.valid = False

        # ── model required fields ──────────────────────────────────────────────
        if "model" in data:
            if not isinstance(data["model"], dict):
                result.errors.append(
                    ValidationIssue(
                        path="model",
                        value=type(data["model"]).__name__,
                        expected="object",
                        severity=Severity.ERROR,
                        message="model must be an object",
                    )
                )
                result.valid = False
            else:
                for mf in ["provider", "name"]:
                    if mf not in data["model"]:
                        result.errors.append(
                            ValidationIssue(
                                path=f"model.{mf}",
                                value=None,
                                expected="present",
                                severity=Severity.ERROR,
                                message=f"Required model field '{mf}' missing",
                            )
                        )
                        result.valid = False
                if "temperature" in data.get("model", {}):
                    t = data["model"]["temperature"]
                    if not (0 <= t <= 2):
                        result.errors.append(
                            ValidationIssue(
                                path="model.temperature",
                                value=t,
                                expected="0 <= temperature <= 2",
                                severity=Severity.ERROR,
                                message=f"temperature={t} out of range [0, 2]",
                            )
                        )
                        result.valid = False

        # ── capabilities ───────────────────────────────────────────────────────
        if "capabilities" in data:
            if not isinstance(data["capabilities"], list):
                result.errors.append(
                    ValidationIssue(
                        path="capabilities",
                        value=type(data["capabilities"]).__name__,
                        expected="array",
                        severity=Severity.ERROR,
                        message="capabilities must be an array",
                    )
                )
                result.valid = False
            elif len(data["capabilities"]) == 0:
                result.errors.append(
                    ValidationIssue(
                        path="capabilities",
                        value=[],
                        expected="minItems=1",
                        severity=Severity.ERROR,
                        message="capabilities cannot be empty",
                    )
                )
                result.valid = False
            else:
                if len(data["capabilities"]) != len(set(str(c) for c in data["capabilities"])):
                    dupes = [
                        c for c in data["capabilities"] if list(str(x) for x in data["capabilities"]).count(str(c)) > 1
                    ]
                    result.warnings.append(
                        ValidationIssue(
                            path="capabilities",
                            value=dupes[:5],
                            expected="uniqueItems",
                            severity=Severity.WARNING,
                            message=f"Duplicate capabilities found: {set(dupes)}",
                        )
                    )
                for cap in data["capabilities"]:
                    if not isinstance(cap, str) or len(cap) < 3:
                        result.errors.append(
                            ValidationIssue(
                                path="capabilities[]",
                                value=cap,
                                expected="string minLength=3",
                                severity=Severity.ERROR,
                                message=f"Invalid capability: {cap!r}",
                            )
                        )
                        result.valid = False

        # ── tools ─────────────────────────────────────────────────────────────
        if "tools" in data:
            if not isinstance(data["tools"], list):
                result.errors.append(
                    ValidationIssue(
                        path="tools",
                        value=type(data["tools"]).__name__,
                        expected="array",
                        severity=Severity.ERROR,
                        message="tools must be an array",
                    )
                )
                result.valid = False
            else:
                for tool in data["tools"]:
                    if not isinstance(tool, str):
                        result.errors.append(
                            ValidationIssue(
                                path="tools[]",
                                value=tool,
                                expected="string",
                                severity=Severity.ERROR,
                                message=f"Invalid tool: {tool!r}",
                            )
                        )
                        result.valid = False

        # ── rules ─────────────────────────────────────────────────────────────
        if "rules" in data:
            if not isinstance(data["rules"], list) or len(data["rules"]) == 0:
                result.errors.append(
                    ValidationIssue(
                        path="rules",
                        value=data.get("rules"),
                        expected="non-empty array",
                        severity=Severity.ERROR,
                        message="rules cannot be empty",
                    )
                )
                result.valid = False

        # ── output_schema ─────────────────────────────────────────────────────
        if "output_schema" in data:
            oschema = data["output_schema"]
            if not isinstance(oschema, dict):
                result.errors.append(
                    ValidationIssue(
                        path="output_schema",
                        value=type(oschema).__name__,
                        expected="object",
                        severity=Severity.ERROR,
                        message="output_schema must be an object",
                    )
                )
                result.valid = False
            else:
                for rf in ["signal", "confidence", "reasoning"]:
                    if rf not in oschema:
                        result.warnings.append(
                            ValidationIssue(
                                path=f"output_schema.{rf}",
                                value=None,
                                expected="present",
                                severity=Severity.WARNING,
                                message=f"Recommended field '{rf}' missing from output_schema",
                            )
                        )

        # ── jsonschema validation (if available) ──────────────────────────────
        if JSONSCHEMA_AVAILABLE and data:
            try:
                jsonschema.validate(data, self.schema)
            except jsonschema.ValidationError as e:
                result.valid = False
                path = ".".join(str(p) for p in e.path) if e.path else "<root>"
                result.errors.append(
                    ValidationIssue(
                        path=path,
                        value=str(e.instance)[:80] if e.instance else None,
                        expected=e.schema.get("description", e.message)[:100],
                        severity=Severity.ERROR,
                        message=e.message[:200],
                    )
                )
            except jsonschema.SchemaError as e:
                result.errors.append(
                    ValidationIssue(
                        path="<schema>",
                        value=str(e)[:100],
                        expected="valid schema",
                        severity=Severity.ERROR,
                        message=f"Schema error: {e.message[:200]}",
                    )
                )
                result.valid = False

        # ── KARL compliance check ──────────────────────────────────────────────
        if "compliance" in data and data["compliance"].get("karllike"):
            for field_name in ["capabilities", "tools", "rules", "output_schema"]:
                if field_name not in data:
                    result.warnings.append(
                        ValidationIssue(
                            path="compliance.karllike",
                            value=True,
                            expected=field_name,
                            severity=Severity.WARNING,
                            message=f"KARL agent missing required field: {field_name}",
                        )
                    )

        return result

    def validate_directory(self, dir_path: Path, recursive: bool = False) -> ValidationReport:
        """Validate all agent.yaml files in a directory."""
        report = ValidationReport()
        for yaml_file in sorted(dir_path.rglob("agent.yaml") if recursive else dir_path.glob("agent.yaml")):
            result = self.validate_file(yaml_file)
            report.results.append(result)
            report.total += 1
            if result.valid:
                report.passed += 1
            else:
                report.failed += 1
            report.warning_count += len(result.warnings)
        return report

    def validate_all(self, base_dir: Path | None = None) -> ValidationReport:
        """Validate entire exported_agents/ folder."""
        base = Path(base_dir) if base_dir else self._find_exported_agents()
        return self.validate_directory(base, recursive=True)

    def _find_exported_agents(self) -> Path:
        candidates = [
            Path("integrations/gitagent"),
            Path("exported_agents"),
        ]
        for p in candidates:
            if p.exists():
                return p
        raise FileNotFoundError("integrations/gitagent/ not found")

    def print_report(self, report: ValidationReport, verbose: bool = False):
        """Print a beautiful colored validation report."""
        print()
        print(c("═" * 70, BLUE))
        print(c("  GitAgent YAML Validator  •  ATOM-VALIDATE-001", BOLD + BLUE))
        print(c("═" * 70, BLUE))
        print()

        # Summary bar
        status_color = GREEN if report.failed == 0 else RED
        status_icon = "✅" if report.failed == 0 else "❌"
        print(f"  {status_icon} {c('VALIDATION REPORT', BOLD + status_color)}")
        print(
            f"     Total:   {report.total}   {c(f'Passed: {report.passed}', GREEN)}   {c(f'Failed: {report.failed}', RED if report.failed > 0 else GREEN)}   {c(f'Warnings: {report.warning_count}', YELLOW)}"
        )
        print()

        if report.failed == 0 and not verbose:
            print(c("  All agents passed validation! ✅", GREEN))
            print()
            return

        for res in report.results:
            agent_color = GREEN if res.valid else RED
            icon = "✅" if res.valid else "❌"
            print(f"  {icon} {c(res.agent_name, agent_color + BOLD)}")

            for err in res.errors:
                print(f"     {c('ERROR', RED)}   {err.path}: {err.message}")
                if err.expected:
                    print(f"            Expected: {err.expected}")

            for warn in res.warnings:
                print(f"     {c('WARN', YELLOW)}   {warn.path}: {warn.message}")

            if verbose:
                for info in res.infos:
                    print(f"     {c('INFO', BLUE)}   {info.path}: {info.message}")

            print()

        print(c("═" * 70, BLUE))
        if report.failed == 0:
            print(c("  ALL VALIDATIONS PASSED ✅", GREEN + BOLD))
        else:
            print(c(f"  {report.failed} AGENT(S) FAILED VALIDATION ❌", RED + BOLD))
        print(c("═" * 70, BLUE))
        print()


def run_validation(strict: bool = False, all_agents: bool = False, dir_path: str | None = None):
    """CLI entry point."""
    try:
        v = AgentYamlValidator()
    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    if dir_path:
        report = v.validate_directory(Path(dir_path))
    elif all_agents:
        report = v.validate_all()
    else:
        # Default: validate exported_agents/
        try:
            report = v.validate_all()
        except FileNotFoundError:
            print(f"{YELLOW}exported_agents/ not found. Validating integrations/gitagent/...{RESET}")
            report = v.validate_all(Path("integrations/gitagent"))

    v.print_report(report, verbose=strict)

    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitAgent YAML Validator")
    parser.add_argument("--dir", "-d", help="Directory to validate")
    parser.add_argument("--all", "-a", action="store_true", help="Validate exported_agents/")
    parser.add_argument("--strict", "-s", action="store_true", help="Verbose output")
    args = parser.parse_args()

    sys.exit(run_validation(strict=args.strict, all_agents=args.all, dir_path=args.dir))
