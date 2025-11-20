from typing import Dict
from abc import abstractmethod
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

    @abstractmethod
    def get_replic_to(situation: Dict[str, any]) -> str:
        # idea is to give implementator the power to
        # give any context he wants to implement logic for
        # given character. For example we can give this
        # characher situation like this: {
        #     "from_director" = "Do some stuff and also youre being punched in the face right now",
        #     "to_you" = "@name, eat shit and also eat shit",
        # }
        pass


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
