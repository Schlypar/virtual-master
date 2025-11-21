from typing import Dict
from .character import Character, Stats
from ...core.agent import Agent


class MCharacter(Character):
    def __init__(
            self,
            name: str,
            stats: Stats,
            background: str,
            aspects: [str],
            agent: Agent
    ):
        super().__init__(name, stats, background, aspects)
        # somehow this particular agent must be heavily coupled
        # with this class and must know about this character as
        # this agent must be roleplaying as this character
        self.agent = agent

    def get_replic_to(self, instruction: str) -> str:
        message = f"""
        You're given this instruction: {instruction}.
        Your response: 
        """
        return self.agent.generate_reply(message)


class NPC(MCharacter):
    def __init__(
            self,
            name: str,
            stats: Stats,
            template: str,
            aspects: [str],
            agent: Agent,
    ):
        super().__init__(name, stats, template, aspects, agent)
