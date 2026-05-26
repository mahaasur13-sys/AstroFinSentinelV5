from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs" / "architecture"

def test_data_flow_md_exists():
    assert (DOCS / "data-flow.md").exists(), "data-flow.md not found"

def test_data_flow_has_required_sections():
    path = DOCS / "data-flow.md"
    if not path.exists():
        return  # handled by first test
    content = path.read_text()
    required = [
        "User Query",
        "Router",
        "Thompson",
        "Parallel",
        "Synthesis",
        "Risk",
        "Execution",
        "Feedback Loop",
        "Meta-RL Flow"
    ]
    for section in required:
        assert section.lower() in content.lower(), f"Missing section: {section}"

def test_component_catalog_exists():
    assert (DOCS / "component-catalog.md").exists(), "component-catalog.md not found"

def test_component_catalog_has_subsystems():
    path = DOCS / "component-catalog.md"
    if not path.exists():
        return
    content = path.read_text()
    # Проверяем, что упомянуты все 7 подсистем из плана
    subsystems = [
        "Presentation Layer",
        "Orchestration Layer",
        "Agent Layer",
        "Core Services Layer",
        "Meta-Learning Layer",
        "Trading Layer",
        "Data Layer"
    ]
    for sub in subsystems:
        assert sub.lower() in content.lower(), f"Missing subsystem: {sub}"

def test_component_catalog_has_agent_weights():
    path = DOCS / "component-catalog.md"
    if not path.exists():
        return
    content = path.read_text()
    # Из плана требуется таблица весов агентов
    assert "Fundamental" in content
    assert "Quant" in content
    assert "Astro" in content
    assert "10%" in content or "weight" in content.lower()
