"""Health check, metrics, and KARL diagnostics endpoints."""
import os, time, psutil, asyncpg, redis.asyncio as aioredis
from typing import Dict
from fastapi import FastAPI, HTTPException
from prometheus_client import generate_latest, REGISTRY
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

import tools.metrics_server

app = FastAPI(title="AstroFin Sentinel — Health & Metrics")
process = psutil.Process(os.getpid())

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime_seconds: float
    memory_mb: float
    cpu_percent: float
    version: str = "5.0.0"

_start_time = time.time()

@app.on_event("startup")
async def startup_event():
    from core.logging import setup_logging
    setup_logging()

async def check_postgres() -> bool:
    try:
        conn = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            user=os.getenv("POSTGRES_USER", "astrofin"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            database=os.getenv("POSTGRES_DB", "astrofin"),
            timeout=5.0,
        )
        await conn.close()
        return True
    except Exception:
        return False

async def check_redis() -> bool:
    try:
        redis_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}"
        r = aioredis.from_url(redis_url, socket_connect_timeout=3)
        await r.ping()
        await r.close()
        return True
    except Exception:
        return False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        uptime_seconds=time.time() - _start_time,
        memory_mb=process.memory_info().rss / 1024 / 1024,
        cpu_percent=process.cpu_percent(interval=0.1),
    )

@app.get("/health/ready")
async def readiness_check():
    pg_ok = await check_postgres()
    redis_ok = await check_redis()
    if pg_ok and redis_ok:
        return {"status": "ready", "timestamp": time.time()}
    else:
        raise HTTPException(status_code=503, detail={
            "postgres": "ok" if pg_ok else "fail",
            "redis": "ok" if redis_ok else "fail",
        })

@app.get("/metrics")
async def metrics_endpoint():
    return PlainTextResponse(
        content=generate_latest(REGISTRY).decode(),
        media_type="text/plain"
    )

@app.get("/metrics/karl")
async def karl_metrics():
    try:
        from agents.karl_synthesis import get_karl_agent
        agent = get_karl_agent()
        status = agent.get_status()
        diag = status.get("karl_diagnostics", {})
        oap = diag.get("oap_kpi", {})
        audit = diag.get("audit_summary", {})
        calibr = diag.get("calibration", {})
        drift = diag.get("drift_status", {})
        class KARLMetrics(BaseModel):
            oos_fail_rate: float
            entropy_avg: float
            grounding_strength: float
            current_ttc_depth: int
            total_decisions: int
            avg_confidence: float
            action_distribution: Dict[str, int]
            calibration_error: float
            slope: float
            intercept: float
            drift_status: str
            confidence_drift: float
            uncertainty_drift: float
            win_rate: float
            sharpe_ratio: float
            max_drawdown: float
            total_trades: int
        return KARLMetrics(
            oos_fail_rate=oap.get("oos_fail_rate", 0.0),
            entropy_avg=oap.get("entropy_avg", 0.0),
            grounding_strength=oap.get("grounding_strength", 0.0),
            current_ttc_depth=oap.get("current_ttc_depth", 0),
            total_decisions=audit.get("total", 0),
            avg_confidence=audit.get("avg_confidence_final", 0.0),
            action_distribution=audit.get("action_distribution", {}),
            calibration_error=calibr.get("calibration_error", 0.0),
            slope=calibr.get("slope", 0.0),
            intercept=calibr.get("intercept", 0.0),
            drift_status=drift.get("status", "unknown"),
            confidence_drift=drift.get("confidence_drift", 0.0),
            uncertainty_drift=drift.get("uncertainty_drift", 0.0),
            win_rate=diag.get("win_rate", 0.0),
            sharpe_ratio=diag.get("sharpe_ratio", 0.0),
            max_drawdown=diag.get("max_drawdown", 0.0),
            total_trades=diag.get("total_trades", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/metrics/system")
async def system_metrics():
    return {
        "memory_percent": process.memory_percent(),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(interval=0.1),
        "num_threads": process.num_threads(),
        "open_files": len(process.open_files()),
        "connections": len(process.connections()),
    }

@app.get("/")
async def root():
    return {"service": "AstroFin Sentinel V5", "version": "5.0.0", "status": "running", "docs": "/docs"}
#!/usr/bin/env python3
"""FastAPI health & metrics endpoints for AstroFin Sentinel V5."""

import os
import secrets
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader

app = FastAPI(title="AstroFin Sentinel — Health & Metrics")

# ── P0 Auth: API Key dependency ────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """Validate X-API-Key header against ASTROFIN_API_KEY env variable."""
    expected = os.getenv("ASTROFIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=401, detail="Authentication not configured")
    if not api_key or not secrets.compare_digest(api_key, expected):
        raise HTTPException(status_code=401 if not api_key else 403,
                            detail="Invalid API key")
    return api_key

# ── Public endpoints (no auth) ─────────────────────────────────────────
@app.get("/")
async def root():
    return {"service": "astrofin-sentinel-health", "status": "UP"}

@app.get("/ready")
async def ready():
    return {"status": "READY"}

# ── Protected endpoints ────────────────────────────────────────────────
@app.get("/health", dependencies=[Depends(verify_api_key)])
async def health():
    """System health check (requires API key)."""
    return {
        "status": "OK",
        "components": {
            "api": "UP",
            "postgres": _check_postgres(),
            "redis": _check_redis(),
        }
    }

@app.get("/metrics/export", dependencies=[Depends(verify_api_key)])
async def export_metrics():
    """Return current Prometheus metrics (requires API key)."""
    # Здесь твоя логика экспорта метрик
    return {"metrics": "exported"}

# ── Helper checks ──────────────────────────────────────────────────────
def _check_postgres():
    # твоя реализация
    return "UP"

def _check_redis():
    # твоя реализация
    return "UP"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
