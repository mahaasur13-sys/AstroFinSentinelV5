"""integrations/gitagent/commit_generator.py — ATOM-GITAGENT-003: Commit Message Generator

Generates meaningful commit messages using MASFactory + KARL analysis.
Analyzes code changes and produces conventional commit messages.
"""
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Conventional Commits types
COMMIT_TYPES = {
    "feat": "Новая функциональность",
    "fix": "Исправление ошибки",
    "perf": "Улучшение производительности",
    "refactor": "Рефакторинг кода",
    "test": "Добавление/изменение тестов",
    "docs": "Документация",
    "chore": "Настройка CI/CD, зависимостей",
    "db": "Изменения в базе данных",
    "security": "Безопасность",
    "revert": "Откат предыдущего изменения",
}


@dataclass
class FileChange:
    """Represents a single file change."""
    path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0
    old_path: Optional[str] = None


@dataclass 
class ChangeSet:
    """Collection of changes for a commit."""
    files: List[FileChange] = field(default_factory=list)
    branch: str = ""
    parent_commit: str = ""
    diff_content: str = ""
    
    def summary(self) -> Dict[str, Any]:
        total_add = sum(f.additions for f in self.files)
        total_del = sum(f.deletions for f in self.files)
        change_types = {}
        for f in self.files:
            change_types[f.change_type] = change_types.get(f.change_type, 0) + 1
        
        extensions: Dict[str, List[str]] = {}
        for f in self.files:
            ext = Path(f.path).suffix or "(no ext)"
            if ext not in extensions:
                extensions[ext] = []
            extensions[ext].append(f.path)
        
        return {
            "total_files": len(self.files),
            "total_additions": total_add,
            "total_deletions": total_del,
            "change_types": change_types,
            "extensions": {k: len(v) for k, v in extensions.items()},
            "top_files": [f.path for f in self.files[:5]],
        }


@dataclass
class CommitMessage:
    """Generated commit message."""
    type: str
    scope: str
    subject: str
    body: str
    footer: str
    breaking: bool
    kar_score: float  # KARL confidence score (0-1)
    reasoning: str
    
    def to_string(self) -> str:
        msg = f"{self.type}"
        if self.scope:
            msg += f"({self.scope})"
        if self.breaking:
            msg += "!"
        msg += f": {self.subject}"
        if self.body:
            msg += f"\n\n{self.body}"
        if self.footer:
            msg += f"\n\n{self.footer}"
        return msg


def get_git_changes(ref: Optional[str] = None) -> ChangeSet:
    """Get list of changed files from git diff."""
    changeset = ChangeSet()
    
    try:
        # Get branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=10
        )
        changeset.branch = result.stdout.strip()
    except Exception:
        changeset.branch = "unknown"
    
    try:
        # Get diff
        ref = ref or "HEAD"
        result = subprocess.run(
            ["git", "diff", "--cached", ref, "--stat", "--numstat"],
            capture_output=True, text=True, timeout=30
        )
        
        for line in result.stdout.strip().split("\n"):
            if not line or "\t" not in line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                path = parts[2]
                
                # Detect change type
                if additions > 0 and deletions == 0:
                    change_type = "added"
                elif deletions > 0 and additions == 0:
                    change_type = "deleted"
                elif deletions > 0:
                    change_type = "modified"
                else:
                    change_type = "modified"
                
                changeset.files.append(FileChange(
                    path=path,
                    change_type=change_type,
                    additions=additions,
                    deletions=deletions,
                ))
        
        # Get diff content for analysis
        diff_result = subprocess.run(
            ["git", "diff", "--cached", ref],
            capture_output=True, text=True, timeout=60
        )
        changeset.diff_content = diff_result.stdout[:5000]  # limit for performance
        changeset.parent_commit = ref or "HEAD"
        
    except Exception:
        pass  # Return empty changeset
    
    return changeset


def detect_scope(changeset: ChangeSet) -> str:
    """Detect the scope (area) of changes."""
    if not changeset.files:
        return "core"
    
    # Analyze file paths
    path_parts: List[Tuple[str, int]] = []
    for f in changeset.files:
        parts = Path(f.path).parts
        if len(parts) > 1:
            path_parts.append((parts[0], len(parts)))
    
    # Most common top-level directory
    from collections import Counter
    top_dirs = Counter(p[0] for p in path_parts)
    if top_dirs:
        return top_dirs.most_common(1)[0][0]
    
    return "core"


def detect_type(changeset: ChangeSet) -> str:
    """Detect the type of change based on files."""
    if not changeset.files:
        return "chore"
    
    # Type detection rules
    patterns = {
        "feat": [r"^agents/.*_agent\.py$", r"^orchestration/.*\.py$", r"^mas_factory/.*\.py$"],
        "fix": [r"fix.*\.py$", r"patch.*\.py$"],
        "test": [r"^tests/", r"^.*_test\.py$", r"^.*_spec\.py$"],
        "docs": [r"\.md$", r"\.rst$", r"\.txt$"],
        "db": [r"^db/", r"^schema/", r"^.*migration.*\.py$", r"\.sql$"],
        "security": [r"auth", r"token", r"secret", r"credential"],
        "perf": [r"cache", r"optim", r"perf", r"speed"],
        "refactor": [r"refactor", r"rename", r"extract"],
    }
    
    scores: Dict[str, int] = {t: 0 for t in patterns}
    scores["chore"] = 0
    
    for f in changeset.files:
        path = f.path.lower()
        content_hints = ""
        
        # Content-based detection
        if "test" in path or "_test" in path:
            scores["test"] += 3
        if "docs" in path or "readme" in path or path.endswith(".md"):
            scores["docs"] += 3
        if "db" in path or "schema" in path or path.endswith(".sql"):
            scores["db"] += 3
        
        for change_type, regexes in patterns.items():
            for regex in regexes:
                if re.search(regex, path, re.IGNORECASE):
                    scores[change_type] += 1
        
        # Added files with new code
        if f.change_type == "added" and f.additions > 30:
            scores["feat"] += 1
    
    # Default to chore if no clear signal
    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        best_type = "chore"
    
    return best_type


def generate_subject(changeset: ChangeSet, change_type: str) -> str:
    """Generate the commit subject line."""
    summary = changeset.summary()
    
    # Scope
    scope = detect_scope(changeset)
    
    # Subject template based on type
    subjects = {
        "feat": ["Add {feature}", "Implement {feature}", "Introduce {feature}"],
        "fix": ["Fix {issue}", "Resolve {issue}", "Patch {issue}"],
        "test": ["Add tests for {area}", "Extend test coverage for {area}"],
        "docs": ["Document {area}", "Update docs for {area}"],
        "db": ["Update database schema for {area}", "Migrate {area} database"],
        "security": ["Improve security in {area}", "Harden {area}"],
        "perf": ["Optimize {area} performance", "Speed up {area}"],
        "refactor": ["Refactor {area}", "Restructure {area}"],
        "chore": ["Update {area}", "Improve {area}", "Polish {area}"],
    }
    
    templates = subjects.get(change_type, subjects["chore"])
    template = templates[0]
    
    # Detect what was changed
    top_files = summary["top_files"]
    if top_files:
        main_file = Path(top_files[0]).name.replace(".py", "").replace("_", " ")
    else:
        main_file = scope
    
    subject = template.replace("{feature}", main_file)
    subject = subject.replace("{issue}", main_file)
    subject = subject.replace("{area}", scope)
    
    # Capitalize
    subject = subject.capitalize()
    if len(subject) > 72:
        subject = subject[:69] + "..."
    
    return subject


def generate_body(changeset: ChangeSet, change_type: str) -> str:
    """Generate the commit body with details."""
    summary = changeset.summary()
    
    lines = []
    
    # Changed files
    if summary["total_files"] <= 10:
        lines.append("### Изменённые файлы")
        for f in changeset.files:
            sign = "+" if f.change_type == "added" else "-" if f.change_type == "deleted" else "~"
            lines.append(f"- {sign} {f.path} (+{f.additions}/-{f.deletions})")
    else:
        lines.append(f"### Изменено файлов: {summary['total_files']}")
        lines.append(f"- Добавлено строк: +{summary['total_additions']}")
        lines.append(f"- Удалено строк: -{summary['total_deletions']}")
    
    return "\n".join(lines)


def generate_footer(changeset: ChangeSet) -> str:
    """Generate the commit footer with metadata."""
    lines = []
    
    # KARL decision hash (for traceability)
    if changeset.files:
        data = ";".join(f.path for f in changeset.files[:5])
        decision_hash = hashlib.md5(data.encode()).hexdigest()[:8]
        lines.append(f"Ref: ASTRO-{decision_hash.upper()}")
    
    # Date
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"Date: {date}")
    
    return "\n".join(lines)


def _analyze_with_karl(changeset: ChangeSet) -> Dict[str, Any]:
    """
    Phase 1 KARL analysis: assess complexity and risk of changes.
    Uses lightweight heuristics (full MASFactory would be too heavy for pre-commit).
    """
    summary = changeset.summary()
    
    # Risk factors
    risk_score = 0.0
    factors = []
    
    # File count risk
    if summary["total_files"] > 10:
        risk_score += 0.15
        factors.append(f"many_files:{summary['total_files']}")
    elif summary["total_files"] > 5:
        risk_score += 0.05
    
    # Changes in core
    core_files = [f for f in changeset.files if any(
        f.path.startswith(p) for p in ["core/", "agents/", "orchestration/", "mas_factory/"]
    )]
    if core_files:
        risk_score += 0.20
        factors.append(f"core_changes:{len(core_files)}")
    
    # Database changes = high risk
    db_files = [f for f in changeset.files if f.path.startswith("db/") or f.path.endswith(".sql")]
    if db_files:
        risk_score += 0.25
        factors.append("db_changes")
    
    # Security-sensitive files
    security_files = [f for f in changeset.files if any(
        kw in f.path.lower() for kw in ["auth", "token", "secret", "credential", "password"]
    )]
    if security_files:
        risk_score += 0.30
        factors.append("security_sensitive")
    
    # Normalize
    risk_score = min(risk_score, 1.0)
    confidence = 1.0 - risk_score
    
    return {
        "risk_score": risk_score,
        "confidence": confidence,
        "factors": factors,
        "kar_score": confidence,
    }


def generate_commit_message(
    changes: Optional[Dict[str, Any]] = None,
    ref: Optional[str] = None,
) -> CommitMessage:
    """
    Generate a conventional commit message from git changes.
    
    Args:
        changes: Optional pre-computed ChangeSet or dict with file changes.
                 If None, reads from git.
        ref: Git ref to diff against (default: HEAD)
    
    Returns:
        CommitMessage with type, scope, subject, body, footer
    """
    # Get changes
    if changes is None:
        changeset = get_git_changes(ref)
    elif isinstance(changes, ChangeSet):
        changeset = changes
    else:
        # Dict with file list
        cs = ChangeSet()
        for item in changes.get("files", []):
            cs.files.append(FileChange(
                path=item.get("path", ""),
                change_type=item.get("type", "modified"),
                additions=item.get("additions", 0),
                deletions=item.get("deletions", 0),
            ))
        changeset = cs
    
    # Detect change type
    change_type = detect_type(changeset)
    
    # Detect breaking changes
    breaking = any(
        "BREAKING" in f.path.upper() or
        (hasattr(f, "additions") and f.additions > 0 and 
         changeset.diff_content and "BREAKING CHANGE" in changeset.diff_content)
        for f in changeset.files
    )
    
    # Generate components
    scope = detect_scope(changeset)
    subject = generate_subject(changeset, change_type)
    body = generate_body(changeset, change_type)
    footer = generate_footer(changeset)
    
    # KARL analysis
    karl = _analyze_with_karl(changeset)
    
    return CommitMessage(
        type=change_type,
        scope=scope,
        subject=subject,
        body=body,
        footer=footer,
        breaking=breaking,
        kar_score=karl["kar_score"],
        reasoning=f"Risk: {karl['risk_score']:.2f}, factors: {', '.join(karl['factors']) or 'none'}",
    )


def preview_commit(ref: Optional[str] = None) -> str:
    """Generate and print a preview of the commit message."""
    msg = generate_commit_message(ref=ref)
    print("=" * 60)
    print("COMMIT MESSAGE PREVIEW")
    print("=" * 60)
    print(msg.to_string())
    print("=" * 60)
    print(f"KARL Confidence Score: {msg.kar_score:.0%}")
    print(f"Reasoning: {msg.reasoning}")
    return msg.to_string()
