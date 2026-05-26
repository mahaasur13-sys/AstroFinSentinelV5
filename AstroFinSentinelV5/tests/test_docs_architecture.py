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

def test_communication_patterns_exists():
    assert (DOCS / "communication-patterns.md").exists(), "communication-patterns.md not found"

def test_communication_patterns_has_required_sections():
    path = DOCS / "communication-patterns.md"
    if not path.exists():
        return
    content = path.read_text()
    # Проверяем основные паттерны из плана
    patterns = [
        "Shared-State Message Passing",
        "Parallel Fan-Out",
        "Thompson Sampling",
        "Pressure Field",
        "Weighted Voting",
        "AMRE Audit",
        "Message Bus"
    ]
    for pat in patterns:
        assert pat.lower() in content.lower(), f"Missing pattern: {pat}"

def test_integration_points_exists():
    assert (DOCS / "integration-points.md").exists(), "integration-points.md not found"

def test_integration_points_has_boundaries():
    path = DOCS / "integration-points.md"
    if not path.exists():
        return
    content = path.read_text()
    boundaries = ["Orchestration", "Agents", "Core", "Meta-RL", "Trading", "Knowledge", "MAS Factory"]
    for b in boundaries:
        assert b.lower() in content.lower(), f"Missing boundary: {b}"

def test_state_management_exists():
    assert (DOCS / "state-management.md").exists(), "state-management.md not found"

def test_state_management_has_singletons():
    path = DOCS / "state-management.md"
    if not path.exists():
        return
    content = path.read_text()
    singletons = ["BeliefTracker", "ThompsonSampler", "KARLSynthesisAgent", "AuditLog", "MessageBus", "AgentRegistry"]
    for s in singletons:
        assert s.lower() in content.lower(), f"Missing singleton: {s}"

def test_integration_points_exists():
    assert (DOCS / "integration-points.md").exists(), "integration-points.md not found"

def test_integration_points_has_boundaries():
    path = DOCS / "integration-points.md"
    if not path.exists():
        return
    content = path.read_text()
    boundaries = ["Orchestration", "Agents", "Core", "Meta-RL", "Trading", "Knowledge", "MAS Factory"]
    for b in boundaries:
        assert b.lower() in content.lower(), f"Missing boundary: {b}"

def test_state_management_exists():
    assert (DOCS / "state-management.md").exists(), "state-management.md not found"

def test_state_management_has_singletons():
    path = DOCS / "state-management.md"
    if not path.exists():
        return
    content = path.read_text()
    singletons = ["BeliefTracker", "ThompsonSampler", "KARLSynthesisAgent", "AuditLog", "MessageBus", "AgentRegistry"]
    for s in singletons:
        assert s.lower() in content.lower(), f"Missing singleton: {s}"
