import os
import pytest


@pytest.fixture(autouse=True)
def set_test_api_key(monkeypatch):
    """Ensure API_KEY is set to a test value for all tests."""
    monkeypatch.setenv("API_KEY", "test-secret-key")
    monkeypatch.setenv("REQUIRE_AUTH", "true")
