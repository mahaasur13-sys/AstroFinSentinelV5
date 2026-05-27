FROM python:3.11-slim

WORKDIR /app

# Install system + supervisord
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Requirements
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true
# Additional production packages
RUN pip install --no-cache-dir \
    timescale[psycopg2] \
    fastapi uvicorn \
    prometheus-client \
    psutil \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-aiohttp \
    opentelemetry-instrumentation-fastapi

# App code
COPY . .

# Supervisor config
RUN mkdir -p /var/log/supervisor
COPY deploy/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
