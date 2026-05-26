from core.base_agent import BaseAgent, AgentResponse, SignalDirection

class MacroAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MacroAgent", domain="macro", weight=0.15)

    async def run(self, state):
        return AgentResponse(
            agent_name="MacroAgent",
            signal=SignalDirection.NEUTRAL,
            confidence=50,
            reasoning="Macro analysis stub",
        )

async def run_macro_agent(state: dict) -> dict:
    """Convenience function for orchestration."""
    agent = MacroAgent()
    resp = await agent.run(state)
    return {"macro_agent_signal": resp.to_dict()}
