import os
import pytest
import subprocess
import time


@pytest.fixture(scope="session")
def flask_app():
    """Start Flask app in background with hardcoded API key."""
    env = os.environ.copy()
    env["API_KEY"] = "test-key"  # жёстко задаём ключ
    proc = subprocess.Popen(
        [".venv/bin/python", "-m", "web.wsgi"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    time.sleep(2)
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session")
def redis_client():
    """Test Redis connection."""
    import redis

    return redis.Redis(host="localhost", port=6379, db=15)
