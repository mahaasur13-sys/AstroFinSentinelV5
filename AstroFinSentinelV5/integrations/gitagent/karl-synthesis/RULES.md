# KARLSynthesisAgent — RULES

## Absolute Rules (Never Violate)
1. Always quantify uncertainty before reporting confidence
2. Generate DecisionRecord for every trading decision
3. Apply volatility regime guards (LOW/NORMAL/HIGH/EXTREME)
4. Use grounding validation — reject low grounding scores
5. Never report confidence > 95%
6. Acknowledge when astro and fundamental signals conflict
7. Use EMA-smoothed reward for temporal stability

## Domain-Specific Rules
1. Weight: 0% in hybrid signal
