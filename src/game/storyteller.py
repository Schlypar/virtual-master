from typing import List, Dict, Optional
from .core.interface import Interface
from .scene import Action


class Storyteller:
    """
    The Storyteller acts as a "talking head" that generates narrative descriptions.
    """

    def __init__(self, ai: Interface):
        """
        Initialize the Storyteller with an AI interface.

        Args:
            ai: Interface object for generating descriptions
        """
        self.ai = ai
        self.history: List[Dict[str, str]] = []

    async def narrate_action(self, action: Action) -> str:
        """
        Takes an Action and returns a nicely written narrative description of that action.

        Args:
            action: The Action to narrate

        Returns:
            A narrative description of the action
        """
        # Build context from history
        messages = self.history.copy() if self.history else []

        # Create prompt for narrating the action
        action_str = str(action)
        messages.append({
            "role": "user",
            "content": f"""
            Write a nicely written narrative description of the following action.
            Make it engaging and immersive, as if you are a storyteller narrating a scene.

            Action: {action_str}

            Provide a narrative description of what happens.

            OUTPUT FORMAT:
            [LIST OF CHARACTERS WHO PERCEIVED THIS ACTION]
            @CHARACTER_NAME: his action or replic
            """
        })

        description = await self.ai.extract_text(messages)

        # Add the narration to history
        self.history.append({
            "role": "user",
            "content": f"Action: {action_str}"
        })
        self.history.append({
            "role": "assistant",
            "content": description
        })

        return description

    async def describe_scene(self, scene_description: str) -> str:
        """
        Describe a scene when there is no current action.

        Args:
            scene_description: Information about the current scene

        Returns:
            A narrative description of the scene
        """
        # Build context from history
        messages = self.history.copy() if self.history else []

        messages.append({
            "role": "user",
            "content": f"""
            Write a nicely written narrative description of the current scene.
            Make it engaging and immersive, setting the stage for what might happen next.

            Scene information: {scene_description}

            Provide a narrative description of the scene.

            If you mention some character, then use @CHARACTER_NAME
            """
        })

        description = await self.ai.extract_text(messages)

        # Add the scene description to history
        self.history.append({
            "role": "user",
            "content": f"Scene: {scene_description}"
        })
        self.history.append({
            "role": "assistant",
            "content": description
        })

        return description
