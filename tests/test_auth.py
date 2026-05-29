import pytest
from fastapi.testclient import TestClient
import os

os.environ["API_KEY"] = "test-key-123"
os.environ["REQUIRE_AUTH"] = "true"

from deploy.monitoring.health_endpoints import app as fastapi_app
from web.wsgi import server as flask_app

fastapi_client = TestClient(fastapi_app, raise_server_exceptions=False)
flask_client = flask_app.test_client()

def test_fastapi_unauthenticated_returns_401():
    response = fastapi_client.get("/api/ab/compare")  # защищённый эндпоинт
    assert response.status_code == 401

def test_flask_unauthenticated_returns_401():
    response = flask_client.get("/api/ab/compare")
    assert response.status_code == 401

def test_public_health_returns_200():
    response = fastapi_client.get("/health")
    assert response.status_code == 200

def test_public_metrics_returns_200():
    response = fastapi_client.get("/metrics")
    assert response.status_code == 200
