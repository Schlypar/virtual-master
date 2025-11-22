from typing import Dict, Optional
from .agent import Agent


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    async def send_to_agent(self, agent_id: str, text: str):
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError("agent not found")
        return await agent.generate_reply(text)

    async def broadcast(self, text: str):
        results = {}
        for aid, ag in self.agents.items():
            results[aid] = await ag.generate_reply(text)
        return results
