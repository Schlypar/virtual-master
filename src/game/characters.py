from typing import Dict, Optional, List
from abc import ABC, abstractmethod
from .core.agent import Agent
from .core.interface import Interface

class Stats:
    def __init__(self, stats: Dict[str, int]):
        self.stats = stats

    def get_bonus(self, stat: int) -> int:
        return (stat - 10) // 2


class Character(ABC):
    def __init__(
            self,
            name: str,
            stats: Stats,
            background: str,
            aspects: [str]
    ):
        self.name = name
        self.stats = stats
        self.background = background
        self.aspects = aspects
        pass

    def get_stats(self) -> Stats:
        return self.stats


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

    async def get_replic_to(self, instruction: str) -> str:
        message = f"""
        You're given this instruction: {instruction}.
        Your response:
        """
        return await self.agent.generate_reply(message)

    def erase_last_memory(self):
        self.agent.erase_last_memory()


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


class PCharacter(Character):
    def __init__(
            self,
            name: str,
            stats: Stats,
            background: str,
            aspects: [str],
            ai: Interface
    ):
        super().__init__(name, stats, background, aspects)
        # this ai is simply an interface to one time
        # prompt to chatGPT and thought to be used as
        # check against any stupid or illogical
        # requests from player
        self.ai = ai

    async def judge(
            self,
            request: str,
            history: Optional[List[Dict[str, str]]] = None,
    ) -> (bool, str):
        messages = []
        if history is not None:
            messages = history.copy()
        messages.append({
            "role": "user",
            "content": f"""
                Based on character background and history of conversation decide whether
                given request is adequate and does not contradict the character.
                Write 'yes' or 'positive' if does not contradict and 'no' or 'negative' otherwise.
                If negative then write what is contradicting
                Here's request: {request}.
                Here's background of character: {self.background}
            """
        })
        remarks = await self.ai.extract_text(messages)
        if "yes" in remarks.lower() or "positive" in remarks.lower():
            return (True, remarks)
        return (False, remarks)
