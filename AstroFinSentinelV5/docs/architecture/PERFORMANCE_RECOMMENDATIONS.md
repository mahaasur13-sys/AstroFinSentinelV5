# Performance Recommendations

## Bottlenecks & Fixes

### 1. Backtester Parallelization
ProcessPoolExecutor with max_workers=4
Expected: 4x speedup

### 2. Ollama Connection Pooling
Persistent ollama.Client with keep-alive
Expected: 2x speedup

### 3. Dash Data Caching
Cache with TTL per callback
Expected: 10x reduction in callback CPU

## Resource Scaling
| Component | Current | Recommended |
|-----------|---------|-------------|
| Redis | 512MB | 2GB |
| TimescaleDB | default | 4CPU + 8GB |
| Prometheus | 2GB | 10GB (30-day) |
