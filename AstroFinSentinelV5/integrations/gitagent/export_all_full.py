#!/usr/bin/env python3
"""export_all_full.py — Full GitAgent Format Export for ALL agents"""
from pathlib import Path

import yaml

OUT = Path("integrations/gitagent")

AGENTS = [
    ("TechnicalAgent", "Technical analysis: RSI, MACD, Bollinger, Volume", "technical", 0.10, ["trend_detection","rsi_calculation","macd_analysis","bollinger_bands","volume_profile","support_resistance"], ["Binance_API","technical_indicators"], ["Regime-adaptive thresholds","15% astro bonus via ephemeris"]),
    ("SentimentAgent", "News, social media (X, Reddit), Fear & Greed", "sentiment", 0.10, ["news_sentiment","social_sentiment","fear_greed","on_chain_sentiment"], ["news_api","social_media"], ["Moon sign influences sentiment","Venus = bullish social mood"]),
    ("OptionsFlowAgent", "Options flow, unusual activity, gamma exposure", "options", 0.15, ["options_flow","unusual_activity","gamma_exposure","iv_rank","max_pain"], ["options_api","greeks_calculator"], ["Mercury retrograde = elevated IV","Jupiter = call buying"]),
    ("MarketAnalyst", "Market structure, liquidity zones, orderflow", "technical", 0.10, ["market_structure","liquidity_zones","orderflow","smart_money_detection"], ["market_depth","orderbook"], ["Equal highs/lows = consolidation","Break of structure = trend"]),
    ("RiskAgent", "Volatility-adaptive position sizing + drawdown", "risk", 0.05, ["position_sizing","drawdown_control","volatility_regime","risk_adjusted_returns"], ["volatility_calculator","atr"], ["LOW: 3%, NORMAL: 2%, HIGH: 1%, EXTREME: 0.5%"]),
    ("BullResearcher", "Bullish narrative + strong astro factors", "bullish", 0.05, ["bullish_narrative","strength_identification","opportunity_mapping"], ["news_analysis","on_chain_metrics"], ["Max 3 bullish catalysts","Confidence floor 55"]),
    ("BearResearcher", "Bearish narrative + risk factors", "bearish", 0.05, ["bearish_narrative","risk_identification","threat_mapping"], ["news_analysis","on_chain_metrics"], ["Max 3 bearish catalysts","Confidence ceiling 45"]),
    ("ElectoralAgent", "Muhurta/Electional timing — best entry windows", "electional", 0.03, ["choghadiya","nakshatra_election","muhurta_scanning","abhijit_muhurta"], ["panchanga_calculator","choghadiya_table"], ["Amrita/Shubha = buy","Rahu Kaal = avoid","Abhijit = best"]),
    ("BradleyAgent", "Bradley Siderograph seasonality model for S&P 500", "astro", 0.03, ["bradley_siderograph","seasonality_scoring","planetary_aspect_forecast"], ["Swiss_Ephemeris","bradley_siderograph"], ["Uses Lahiri ayanamsa","S&P 500 specific","Weight 3%"]),
    ("GannAgent", "Gann angles, Square of 9, time/price analysis", "astro", 0.03, ["gann_angles","square_of_9","time_price_squaring","trendline_analysis"], ["gann_geometry","ephemeris"], ["1x1 angle = primary support","Time clusters for reversals"]),
    ("CycleAgent", "Dominant cycles + Jupiter/Saturn astro-cycles", "astro", 0.05, ["cycle_identification","phase_analysis","turning_point_detection","jupiter_saturn_cycles"], ["cycle_analysis","spectral_analysis"], ["Cycle changes = regime shifts","Saturn=bear, Jupiter=bull"]),
    ("ElliotAgent", "Elliott Wave counting + astro correlations", "technical", 0.05, ["wave_counting","wave_personality","fibonacci_retracement","wave_identification"], ["wave_analysis","fibonacci"], ["5-wave impulse = trend","Astro aspects trigger reversals"]),
    ("TimeWindowAgent", "Multi-timeframe entry windows (4H/1D/1W) + astro", "technical", 0.02, ["multi_tf_windows","entry_optimization","time_cluster_detection"], ["multi_timeframe","astro_windows"], ["4H = intraday","1D = swing","1W = positional"]),
    ("InsiderAgent", "Insider activity, 13F filings, whale wallet tracking", "fundamental", 0.05, ["insider_tracking","whale_wallets","13f_filings","fund_flow_analysis"], ["sec_edgar","on_chain_whale_tracking"], ["Whale accumulation = bullish","Insider selling = bearish"]),
    ("MLPredictorAgent", "ML-based price prediction with astro-enhanced features", "quant", 0.05, ["price_prediction","pattern_recognition","regime_classification","astro_features"], ["sklearn","astro_features","price_model"], ["Astro planets as input","Prediction: 4H/1D/1W"]),
    ("FundamentalAgent", "Financial statement analysis, on-chain, MVRV", "fundamental", 0.20, ["financial_statements","on_chain_metrics","MVRV_analysis","ATH_distance","valuation"], ["coingecko_api","on_chain_data"], ["Jupiter = expansion","Saturn = contraction"]),
    ("QuantAgent", "ML backtesting, momentum and mean reversion", "quant", 0.20, ["ml_prediction","momentum_strategy","mean_reversion","backtesting","volatility_forecasting"], ["backtesting_engine","ml_models"], ["20% astro weight in ML"]),
    ("MacroAgent", "VIX, DXY, Gold, Fed rates, geopolitical risk", "macro", 0.15, ["vix_analysis","dxy_impact","gold_correlation","fed_policy","geopolitical_risk"], ["yahoo_finance","fed_data"], ["Saturn = deflationary","Jupiter = inflationary"]),
]

for name, desc, domain, weight, caps, tools, rules in AGENTS:
    pkg = OUT / name.lower().replace("agent","_agent").replace("__","_")
    if not pkg.exists():
        pkg = OUT / name.lower()
    pkg.mkdir(parents=True, exist_ok=True)
    
    # SOUL.md
    soul = f"""# {name} — SOUL

## Identity
You are **{name}** in AstroFin Sentinel V5 multi-agent system.

## Role
{desc}

## Communication Style
- Precise and analytical
- Cite numerical thresholds and values
- Include confidence intervals
- Always explain reasoning step-by-step

## KARL Integration
- All decisions generate DecisionRecords
- Uncertainty quantified before reporting confidence
- AMRE validation applies to all outputs
"""
    (pkg / "SOUL.md").write_text(soul)
    
    # RULES.md
    rules_md = f"""# {name} — RULES

## Absolute Rules
1. Always quantify uncertainty before reporting confidence
2. Generate DecisionRecord for every decision
3. Apply volatility regime guards (LOW/NORMAL/HIGH/EXTREME)
4. Use grounding validation
5. Never report confidence > 95%

## Domain Rules
""" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(rules))
    (pkg / "RULES.md").write_text(rules_md)
    
    # DUTIES.md
    duties = f"""# {name} — DUTIES

## Responsibilities
- Analyze market data for {domain} signals
- Generate trading recommendations with confidence
- Log all decisions for KARL audit trail

## Output Schema
```yaml
signal: LONG | SHORT | NEUTRAL | BUY | SELL | AVOID
confidence: 0-100
reasoning: str
sources: list
metadata:
  weight: {weight}
  domain: {domain}
```

## Capabilities
""" + "\n".join(f"- **{c}**" for c in caps)
    (pkg / "DUTIES.md").write_text(duties)
    
    # agent.yaml
    yaml_dict = {
        "name": name.lower().replace("_agent", "-agent"),
        "description": desc,
        "version": "5.0",
        "model": {"provider": "vercel", "name": "minimax/minimax-m2.7", "temperature": 0.3},
        "capabilities": caps,
        "tools": tools,
        "rules": rules,
        "output_schema": {"signal": "LONG | SHORT | NEUTRAL | BUY | SELL | AVOID", "confidence": "0-100", "reasoning": "str", "sources": "list"},
    }
    (pkg / "agent.yaml").write_text(yaml.dump(yaml_dict, default_flow_style=False))
    
    print(f"✅ {name} ({len(list(pkg.iterdir()))} files)")

print(f"\n✅ Total: {len(AGENTS)} agents exported to GitAgent format")
