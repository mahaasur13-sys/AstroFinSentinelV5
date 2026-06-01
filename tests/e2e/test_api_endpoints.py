import pytest
from web.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.e2e
def test_health_endpoint(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert b"ok" in rv.data
