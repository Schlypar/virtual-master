from typing import Dict
from abc import ABC, abstractmethod


class Stats:
    def __init__(self, stats: Dict[str, int]):
        self.stats = stats

    def get_bonus(self, stat: int) -> int:
        return (stat - 10) // 2
