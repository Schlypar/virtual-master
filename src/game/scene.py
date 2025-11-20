from typing import Dict, Union
from abc import ABC, abstractmethod

from characters.character import Character
from characters.master_character import MCharacter, NPC
from ..core.interface import Interface
from .director import Director, Request, Spotlight


class SceneJudge(ABC):
    def __init__(self, ai: Interface):
        self.ai = ai

    @abstractmethod
    def judge(self, situation: Dict[str, any]):
        # idea is to give implementator the power to
        # give any context he wants to implement logic for
        # what is acceptable in the scene. For example we can
        # give a situation like this: {
        #         "plot" = f"<insert a plot from scene here>",
        #         "request" = "I want to drop atomic bomb instantly from my ass",
        #         ...
        #     }
        pass


def SceneChanger(ABC):
    def __init__(self, plot: str, ai: Interface):
        self.plot = plot
        self.ai = ai

    @abstractmethod
    def is_finished(request: str) -> bool:
        pass


class Scene:
    def __init__(
        self,
        plot: str,
        master_characters: [MCharacter],
        general_npc: NPC,
        director: Director,
        scene_judje: SceneJudge,
        scene_changer: SceneChanger
    ):
        self.plot = plot
        self.master_characters = master_characters
        self.general_npc = general_npc
        self.director = director
        self.scene_judje = scene_judje
        self.scene_changer = scene_changer

    def is_finished(self, request: Request) -> bool:
        return self.scene_changer.is_finished(request)

    def play(self) -> Request:
        pass
