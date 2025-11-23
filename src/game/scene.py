from typing import Dict, Optional, List
from abc import ABC

from .core.interface import Interface
from .core.utils import extract_names

from .characters import Character, PCharacter, MCharacter, NPC
from .director import Director, Request, Spotlight
from .dice import Dice


def draw_bordered_text(text, width):
    """
    Draws a border around text, breaking long lines into multiple parts.

    Args:
        text (str): The text to put in a border
        width (int): The maximum width of each line (including borders)

    Returns:
        str: The text with border
    """
    if width < 5:
        raise ValueError(
            "Width must be at least 5 to accommodate borders and minimal text")

    content_width = width - 4

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Check if adding this word would exceed the line length
        if len(' '.join(current_line + [word])) <= content_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    if not lines:
        lines = [""]

    top_border = "┌" + "─" * (width - 2) + "┐"
    bottom_border = "└" + "─" * (width - 2) + "┘"

    bordered_lines = [top_border]

    for line in lines:
        padded_line = line.ljust(content_width)
        bordered_lines.append(f"│ {padded_line} │")

    bordered_lines.append(bottom_border)

    return '\n'.join(bordered_lines)


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

    async def judge(
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
        if "yes" in remarks.lower() or "positive" in remarks.lower():
            return (True, remarks)
        return (False, remarks)

    async def perception_check(
            self,
            request: Request,
            agents: [Character],
            history: Optional[List[Dict[str, str]]]
    ) -> [str]:
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
        return await self.ai.extract_text(messages)


class SceneChanger(ABC):
    def __init__(self, plot: str, ai: Interface):
        self.plot = plot
        self.ai = ai

    async def is_finished(self, plot: str, history: List[Dict[str, str]]) -> bool:
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
        if "yes" in reply.lower() or "positive" in reply.lower():
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

    async def give_spotlight(self, spotlight: Spotlight) -> Action:
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
                    print(draw_bordered_text(
                        text=f"@Player: {spotlight.to_character}",
                        width=80
                    ))
                    request = input("\nYour action: ")
                    # 1.5. validate that request with PlayerJudge first
                    accepted, remark = await self.player.judge(
                        request,
                        self.director.messages
                    )
                    if accepted:
                        break
                    spotlight.to_character += f"\nSome remarks: {remark}"
            else:
                request = await actor.get_replic_to(
                    spotlight.to_character
                )
                break

            # 2. validate that request with SceneJudge
            accepted, remark = await self.scene_judje.judge(
                request,
                self.director.messages
            )
            if accepted:
                break
            spotlight.to_character += f"\nSome remarks: {remark}"
            if not is_player:
                actor.erase_last_memory()

        # 3. if action must be with difficulty then calculate it and test
        dice = Dice(self.scene_judje.ai)
        context = {
            "plot": self.plot,
            "history": self.director.messages
        }
        check_result = await dice.resolve_action(request, actor, context)

        # Update request string based on difficulty check result
        if check_result["requires_check"]:
            if check_result["modified_action"]:
                # Use the modified action from Dice if available
                request = check_result["modified_action"]
            elif not check_result["success"]:
                # If check failed, modify the request to reflect failure
                if check_result["outcome_modification"]:
                    request = f"{
                        request} (Failed: {check_result['outcome_modification']})"
                else:
                    request = f"{request} (Failed)"
            else:
                # If check succeeded, optionally add success indicator
                if check_result["outcome_modification"]:
                    request = f"{
                        request} ({check_result['outcome_modification']})"

        req = Request(actor, request)
        action = Action(req, [actor])
        # 4. Judge also must give who perceived this action after difficulty testing was done
        perceived = extract_names([await self.scene_judje.perception_check(
            req,
            self.master_characters,
            self.director.messages
        )])
        # 5. Update memory of all agents who perceived that action.
        for character in self.master_characters:
            if character.name in perceived and character in self.master_characters:
                character.update_memory([action.request.content])

        if not is_player and "Player" in perceived:
            action.perceived_action.append(self.player)
        # 6. return given action to next level
        return action
