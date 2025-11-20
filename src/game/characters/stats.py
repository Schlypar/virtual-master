from typing import Dict
from abc import ABC, abstractmethod


class Stats(ABC):
    def __init__(self, stats: Dict[str, int]):
        self.stats = stats

    @abstractmethod
    def get_bonus(stat: int) -> int:
        pass
