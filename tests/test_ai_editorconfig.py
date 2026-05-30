import os
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_cursorrules_exists():
    assert (ROOT / ".cursorrules").exists(), ".cursorrules not found"


def test_claude_md_exists():
    assert (ROOT / "CLAUDE.md").exists(), "CLAUDE.md not found"


def test_cursorrules_references_agents_md():
    content = (ROOT / ".cursorrules").read_text()
    assert "AGENTS.md" in content, ".cursorrules should reference AGENTS.md"


def test_claude_md_references_agents_md():
    content = (ROOT / "CLAUDE.md").read_text()
    assert "AGENTS.md" in content, "CLAUDE.md should reference AGENTS.md"
