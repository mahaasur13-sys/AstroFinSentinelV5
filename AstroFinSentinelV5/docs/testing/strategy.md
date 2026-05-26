# AstroFinSentinelV5 — Testing Strategy

**ATOM-META-RL-024 | Phase 6: Testing and Validation**

---

## Unit Tests (Target: 80% coverage)

- Core math: `KeplerOrbit.solve_kepler()`, `compute_astro_reward()`, reward formula calculations
- Risk engine: All `RiskEngineV2` methods with edge cases (NaN, boundary, overflow)
- Belief updates: Beta distribution updates, cold start behavior, history trimming
- Thompson sampling: Selection logic, exploration bonus, pool mappings

## Integration Tests (Target: Key Paths)

- Full orchestration flow: Query → Router → Selection → Agents → Synthesis → Response
- Belief feedback loop: Session completion → Belief update → Selection impact verification
- Meta-RL cycle: Evolution → Persistence → Load → Resume verification
- Safety gate: Mode enforcement, risk check, sanity validation

## System Tests (Target: Critical Scenarios)

- Multi-agent consensus scenarios (unanimous, split, conflict)
- Risk gate rejection scenarios (kill switch, exposure limit, correlation)
- Graceful degradation (Ollama down, ephemeris down, broker down)
- End-to-end paper trading with real broker API

---

## Validation Stages

### Stage 1: Historical Backtest Validation
- Minimum 2 years of historical data per symbol
- Walk-forward validation with 70/30 train/test splits
- Overfitting detection: Sharpe degradation < 30% between IS and OOS
- Required metrics: Win rate > 50%, Sharpe > 1.0, Max drawdown < 15%

### Stage 2: Paper Trading Validation
- Minimum 30 calendar days on testnet
- Compare paper results to backtest projections (within 2σ tolerance)
- Monitor for look-ahead bias indicators (suspiciously high win rate)
- Track slippage simulation accuracy vs paper fills

### Stage 3: Live Limited Validation
- Position size capped at 5% of NAV
- Maximum 5 trades per day
- 14-day minimum observation period
- Automatic pause if drawdown exceeds 10% of allocated capital

### Stage 4: Live Full Deployment
- Gradual position size increase: 5% → 10% → 20% over 4 weeks
- Continuous monitoring with alerting on anomalies
- Weekly performance review against benchmarks
