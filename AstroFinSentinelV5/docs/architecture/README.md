# AstroFinSentinelV5 — System Architecture

**Version:** 5.0 | **Updated:** 2026-05-26

## Overview

AstroFinSentinelV5 is a Meta-RL platform for autonomous trading strategy evolution.

## Modules

| Module | Responsibility |
|-------|---------------|
| core/ | Data, signals, portfolio |
| orchestration/ | LangGraph pipeline |
| agents/ | LLM agents (Karl, Synthesis) |
| meta_rl/ | Evolution, persistence, intelligence (30+ files) |
| trading/ | Backtester, risk, portfolio |
| web/ | Dash dashboard |
| training/ | Walk-forward, metrics |

## Architecture Notes

- **Persistence** — MetaRLPersistence with JSON + file storage
- **LLM** — Ollama (local) with llama3:8b, qwen2.5-coder:7b
- **Dashboard** — Dash 4.x with Plotly dark theme
- **Container** — Supervisord-managed multi-process inside Docker
