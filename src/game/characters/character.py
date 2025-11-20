from abc import ABC
from .stats import Stats


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
