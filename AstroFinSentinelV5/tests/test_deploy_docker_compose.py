import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
COMPOSE_FILE = ROOT / "deploy" / "docker" / "docker-compose.yml"

def test_jaeger_service_present():
    """Jaeger сервис должен быть определён в docker-compose."""
    if not COMPOSE_FILE.exists():
        return
    with open(COMPOSE_FILE) as f:
        compose = yaml.safe_load(f)
    services = compose.get("services", {})
    assert "jaeger" in services, "Jaeger service missing"
    jaeger = services["jaeger"]
    assert jaeger["image"].startswith("jaegertracing/all-in-one")
    ports = jaeger.get("ports", [])
    assert any("16686" in p for p in ports), "Jaeger UI port 16686 not exposed"
    assert any("4317" in p for p in ports), "OTLP gRPC port 4317 not exposed"
