# tests/test_auth_middleware.py
import pytest

from web.wsgi import server


@pytest.fixture
def client():
    server.config["TESTING"] = True
    with server.test_client() as c:
        yield c


def test_protected_endpoint_requires_auth(client):
    """Без заголовка X-API-Key защищённый эндпоинт возвращает 401."""
    resp = client.post("/api/live/enable", json={"confirmed": True})
    assert resp.status_code == 401


def test_protected_endpoint_rejects_wrong_key(monkeypatch, client):
    """С неверным ключом возвращает 403, если ключ настроен."""
    monkeypatch.setenv("ASTROFIN_API_KEY", "correct-key")
    resp = client.post(
        "/api/live/enable", json={"confirmed": True}, headers={"X-API-Key": "wrong-key"}
    )
    assert resp.status_code == 403


def test_protected_endpoint_accepts_valid_key(monkeypatch, client):
    """С верным ключом аутентификация проходит (не 401/403)."""
    monkeypatch.setenv("ASTROFIN_API_KEY", "test-key")
    resp = client.post(
        "/api/live/enable", json={"confirmed": True}, headers={"X-API-Key": "test-key"}
    )
    # Не должно быть ошибки аутентификации
    assert resp.status_code not in (401, 403)
