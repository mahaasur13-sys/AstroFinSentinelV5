import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "test-key"
API_KEY = "test-key"


@pytest.mark.e2e
def test_health_endpoint(flask_app):
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "X-RateLimit-Remaining" in resp.headers


@pytest.mark.e2e
def test_rate_limiting(flask_app):
    for i in range(15):
        resp = requests.get(f"{BASE_URL}/api/ab/compare", headers={"X-API-Key": API_KEY})
        if resp.status_code == 429:
            break
    assert resp.status_code == 429
    if resp.status_code == 401:
        pytest.skip("Server not ready")
