from typing import Dict, Optional, List
from abc import ABC, abstractmethod

from characters.character import Character
from characters.player_character import PCharacter
from characters.master_character import MCharacter, NPC
from ..core.interface import Interface
from .director import Director, Request, Spotlight
from ..core.utils import extract_names


class Action:
    def __init__(self, request: Request, perceived_action: [Character]):
        self.request = request
        self.perceived_action = perceived_action

    def __str__(self):
        character_names: List[str] = []
        for character in self.perceived_action:
            character_names.append("@" + character.name)
        return f"@{self.request.character.name}: {self.request.content}.\nThis action perceived: {character_names}"


class SceneJudge(ABC):
    def __init__(self, ai: Interface):
        self.ai = ai

    def judge(
            self,
            request: str,
            plot: str,
            history: Optional[List[Dict[str, str]]] = None
    ) -> (bool, str):
        messages = []
        if history is not None:
            messages = history.copy()
        messages.append({
            "role": "user",
            "content": f"""
                Based on script and history of conversation decide whether
                given request is adequate and does not contradict the plot.
                Write 'yes' or 'positive' if does not contradict and 'no' or 'negative' otherwise
                If negative then write what is contradicting
                Here's request: {request}.
                Here's script: {plot}
            """
        })
        remarks = await self.ai.extract_text(messages)
        if "yes" in remarks.to_lower() or "positive" in remarks.to_lower():
            return (True, remarks)
        return (False, remarks)

    def perception_check(
            self,
            request: Request,
            agents: [Character],
            history: Optional[List[Dict[str, str]]]
    ) -> [Character]:
        messages = []
        if history is not None:
            messages = history.copy()

        character_names: List[str] = []
        for character in agents:
            character_names.append(character.name)

        messages.append({
            "role": "user",
            "content": f"""
                Based on request and history of conversation decide which
                characters are perceived this action by {request.character.name} and @Player.
                Write List of Names starting with @ (example @Jack) separated by commas.
                Here's request: {request.content}.
                Here's all possible agenst: {character_names}
            """
        })
        reply = await self.ai.extract_text(messages)


class SceneChanger(ABC):
    def __init__(self, plot: str, ai: Interface):
        self.plot = plot
        self.ai = ai

    def is_finished(self, plot: str, history: List[Dict[str, str]]) -> bool:
        messages = history.copy()
        messages.append({
            "role": "user",
            "content": f"""
            Based on script and history of conversation
            decide if this script is finished.
            Output 'yes' or 'positive' if script is finished otherwise 'no' or 'negative'
            Here's script: {plot}
            """
        })
        reply = await self.ai.extract_text(messages)
        if "yes" in reply.to_lower() or "positive" in reply.to_lower():
            return True
        return False


class Scene(ABC):
    def __init__(
        self,
        plot: str,
        player: PCharacter,
        master_characters: [MCharacter],
        general_npc: NPC,
        director: Director,
        scene_judje: SceneJudge,
        scene_changer: SceneChanger
    ):
        self.plot = plot
        self.player = player
        self.master_characters = master_characters
        self.general_npc = general_npc
        self.director = director
        self.scene_judje = scene_judje
        self.scene_changer = scene_changer

    def is_finished(self, request: Request) -> bool:
        return self.scene_changer.is_finished(self.plot, self.director.messages)

    def get_spotlight(self, story_information: str) -> Spotlight:
        return self.director.give_directive(story_information)

    def give_spotlight(self, spotlight: Spotlight) -> Action:
        is_player = True
        actor: Character = None
        for character in self.master_characters:
            if spotlight.character_name == character.name:
                is_player = False
                actor = character
                break

        if is_player:
            actor = self.player

        while True:
            # 1. get request from character
            request: str = ""
            if is_player:
                while True:
                    request = input(
                        f"{spotlight.to_character}.\nYour action: ")
                    # 1.5. validate that request with PlayerJudge first
                    accepted, remark = self.player.judge(
                        request,
                        self.director.messages
                    )
                    if accepted:
                        break
                    spotlight.to_character += f"\nSome remarks: {remark}"
            else:
                request = MCharacter(actor).get_replic_to(
                    spotlight.to_character
                )

            # 2. validate that request with SceneJudge
            accepted, remark = self.scene_judje.judge(
                request,
                self.director.messages
            )
            if accepted:
                break
            spotlight.to_character += f"\nSome remarks: {remark}"
            if not is_player:
                MCharacter(actor).erase_last_memory()

        # 3. if action must be with difficulty then calculate it and test
        req = Request(actor, request)
        action = Action(req, [actor])
        # TODO: implement logic that defines how difficulty calculated and how it is tested.
        # For now assume that everything is a success
        # 4. Judge also must give who perceived this action after difficulty testing was done
        perceived = extract_names(self.scene_judje.perception_check(
            req,
            self.master_characters,
            self.director.messages
        ))
        # 5. Update memory of all agents who perceived that action.
        for character in self.master_characters:
            if character.name in perceived and character in self.master_characters:
                MCharacter(character).update_memory([action.request.request])

        if not is_player and "Player" in perceived:
            action.perceived_action.append(self.player)
        # 6. return given action to next level
        return action
