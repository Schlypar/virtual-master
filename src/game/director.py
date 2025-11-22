from typing import Dict, List
from .characters import Character
from .core.interface import Interface
from .core.utils import split_string


class Spotlight:
    def __init__(self, character_name: str, to_character: str):
        self.character_name = character_name
        self.to_character = to_character


class Request:
    def __init__(self, character: Character, content: str):
        self.character = character
        self.request = content


class Director:
    def __init__(self, plot: str, ai: Interface):
        self.plot = plot
        self.ai = ai
        # TODO: make this system prompt more clearer to what AI must do
        self.messages: List[Dict[str, str]] = [{
            "role": "system",
            "content": f"""
            You're master in DnD and you will help to move the story for players.
            We will have non-playable character (every name starting from '@' except '@Player')
            to which you should give directives of what they must do. They must do actions in two cases:
              1. when player's action is targeted at them
              2. when it is appropriate to advance the story with help of action of this character

            I will write to you what each character is done and you will write directive based on this.

            You must output only one directive at a time. I will give you actions of characters.

            Directive is not replic or concrete action that character must do.
            It is more a suggestion to the character and action itself does character.

            Here's the script that you are given:
            {plot}
            """
        }]

    async def give_directive(self, story_information: str) -> Spotlight:
        self.messages.append({
            "role": "user",
            "content": story_information
        })
        reply = await self.ai.extract_text(self.messages)
        self.messages.append(reply)
        splitted_str = split_string(reply)
        character_name = splitted_str[0][1:]
        content = splitted_str[1]
        return Spotlight(character_name, content)
