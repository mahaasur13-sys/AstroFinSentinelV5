# Technical Debt Analysis

## Critical
| Issue | Fix |
|-------|-----|
| No async in backtester | Add asyncio + concurrent.futures |
| Hardcoded Ollama | Add retry wrapper |
| JSON file storage | Switch to sqlite |
| No Redis clustering | Add Sentinel mode |

## High
| Issue | Fix |
|-------|-----|
| No push gateway | prometheus_client.push_to_gateway |
| No circuit breakers | Add circuitbreaker library |
| Dash callbacks not memoized | Add prevent_initial_call |
| No data versioning | Add data/version/ timestamps |
