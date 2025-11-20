from abc import abstractmethod
from .character import Character, Stats
from ...core.interface import Interface


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

    @abstractmethod
    def judge(request: str) -> bool:
        pass
