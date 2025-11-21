from typing import Dict, Optional, List
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

    def judge(
            self,
            request: str,
            history: Optional[List[Dict[str, str]]] = None,
    ) -> (bool, str):
        messages = []
        if history is not None:
            messages = history.copy()
        messages.append({
            "role": "user",
            "content": f"""
                Based on character background and history of conversation decide whether
                given request is adequate and does not contradict the character.
                Write 'yes' or 'positive' if does not contradict and 'no' or 'negative' otherwise.
                If negative then write what is contradicting
                Here's request: {request}.
                Here's background of character: {self.background}
            """
        })
        remarks = await self.ai.extract_text(messages)
        if "yes" in remarks.to_lower() or "positive" in remarks.to_lower():
            return (True, remarks)
        return (False, remarks)
