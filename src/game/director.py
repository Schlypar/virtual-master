from abc import ABC, abstractmethod
from characters.character import Character
from characters.master_character import MCharacter
from characters.player_character import PCharacter
from ..core.interface import Interface


class Spotlight:
    def __init__(self, character: Character, to_character):
        self.character = character
        self.to_character = to_character


class Request:
    def __init__(self, character: Character, to_character):
        self.character = character
        self.request = to_character


class Director(ABC):
    def __init__(self, plot: str, ai: Interface):
        self.plot = plot
        self.ai = ai

    @abstractmethod
    def process_request(self, request: Request, story_information: str) -> Request:
        # example fro start
        if isinstance(request.character, PCharacter):
            pass
        elif isinstance(request.character, MCharacter):
            pass

    @abstractmethod
    def process_from_storyteller(
            self,
            story_information: str,
            to_character: Character,
    ) -> Spotlight:
        pass

    @abstractmethod
    def process_from_judge(
            self,
            request: Request,
            remark: str,
            story_information: str,
    ) -> Request:
        pass
