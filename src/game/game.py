from typing import List, Optional
from .scene import Scene, Action
from .storyteller import Storyteller
from .characters import PCharacter


class Plot:
    """
    Plot is essentially a data structure containing the story and scenes.
    """

    def __init__(self, story: str, scenes: List[Scene]):
        """
        Initialize a Plot with a story and a linear collection of Scene objects.

        Args:
            story: The story description
            scenes: A linear collection of Scene objects
        """
        self.story: str = story
        self.scenes: List[Scene] = scenes


class Game:
    """
    The main Game class that orchestrates the game loop.
    """

    def __init__(self, plot: Plot, player: PCharacter, storyteller: Storyteller):
        """
        Initialize the Game with plot, player, and storyteller.

        Args:
            plot: An instance of Plot
            player: An instance of PCharacter
            storyteller: An instance of Storyteller
        """
        self.plot: Plot = plot
        self.player: PCharacter = player
        self.storyteller: Storyteller = storyteller
        self.current_action: Optional[Action] = None
        self.current_scene_index: int = 0

    def _get_current_scene(self) -> Optional[Scene]:
        """Get the current scene from the plot."""
        if 0 <= self.current_scene_index < len(self.plot.scenes):
            return self.plot.scenes[self.current_scene_index]
        return None

    async def runGame(self):
        """
        Run the main game loop following the specified algorithm:
        1. Start an infinite loop
        2. The storyteller produces a description (scene if no action, action if there is one)
        3. Request a Spotlight from the current Scene using this description
        4. Pass the Spotlight back to the Scene to obtain the next Action
        5. Feed this Action into the storyteller to narrate it
        6. Check whether the Scene has ended - if yes, move to next Scene
        """
        description = ""
        while True:
            current_scene = self._get_current_scene()
            if current_scene is None:
                # No more scenes, end the game
                break

            # Step 1: Storyteller produces a description
            if self.current_action is None:
                # No current action, describe the scene
                scene_info = f"Story: {self.plot.story}\nCurrent scene plot: {
                    current_scene.plot}"
                description = await self.storyteller.describe_scene(scene_info)

            # Step 2: Request a Spotlight from the current Scene using the description
            # Note: Scene.get_spotlight calls director.give_directive which is async,
            # but get_spotlight itself is not async. We need to call the async method directly.
            spotlight = await current_scene.director.give_directive(description)

            # Step 3: Pass the Spotlight back to the Scene to obtain the next Action
            action = await current_scene.give_spotlight(spotlight)

            # Step 4: Feed this Action into the storyteller to narrate it
            # This narration will be used as the description in the next iteration
            description = await self.storyteller.narrate_action(action)
            self.current_action = action

            # Step 5: Check whether the Scene has ended
            # Note: Scene.is_finished calls scene_changer.is_finished which is async,
            # but is_finished itself is not async. We need to call the async method directly.
            # Also, is_finished requires a Request parameter, so we use the action's request
            is_finished = await current_scene.scene_changer.is_finished(
                current_scene.plot,
                current_scene.director.messages
            )

            if is_finished:
                # Move to the next scene in the linear sequence
                self.current_scene_index += 1
                self.current_action = None  # Reset action for new scene
