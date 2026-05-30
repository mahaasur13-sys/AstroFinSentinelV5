"""AstroCouncilAgent stub for backtest integration."""

from core.base_agent import AgentResponse, BaseAgent, SignalDirection


class AstroCouncilAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AstroCouncil", domain="astro", weight=0.10)

    async def run(self, state):
        return {
            "astro_council_signal": AgentResponse(
                agent_name="AstroCouncil",
                signal=SignalDirection.NEUTRAL,
                confidence=50,
                reasoning="Astro council stub: no ephemeris available",
            ).to_dict()
        }
