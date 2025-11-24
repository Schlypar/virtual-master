from typing import List, Dict, Optional
from .core.interface import Interface
from .scene import Action

from colorama import Back, Style

BLACK = '\033[40m'
RED = '\033[41m'
GREEN = '\033[42m'
YELLOW = '\033[43m'
BLUE = '\033[44m'
MAGENTA = '\033[45m'
CYAN = '\033[46m'
WHITE = '\033[47m'
BRIGHT_BLACK = '\033[100m'
BRIGHT_RED = '\033[101m'
BRIGHT_GREEN = '\033[102m'
BRIGHT_YELLOW = '\033[103m'
BRIGHT_BLUE = '\033[104m'
BRIGHT_MAGENTA = '\033[105m'
BRIGHT_CYAN = '\033[106m'
BRIGHT_WHITE = '\033[107m'


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
            Use at most 3 sentences to describe.
            You should try to advance scene more slowly accounting for
            action that is present. Not every action should advance story.
            You can use action to slowly advance the story of the scene.

            Action: {action_str}

            Provide a narrative description of what happens.

            OUTPUT FORMAT:
            *Some actions related to the story*\n
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
        Describe a begining of the scene.
        You should only try to describe the opening of the scene and 
        try not to spoil all the plot before player experiences it!.

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
            Write a nicely written narrative description of a begining the scene.
            Make it engaging and immersive, setting the stage for what might happen next.
            Do not spoil or start at the middle or later parts of the script.
            You should start at the very begining of the scene and then advance the story
            when appropriate.
            Use at most 3 sentences to describe.

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


def create_text_grid(strings: [str], width: int, padding: int = 1) -> str:
    """
    Create a text grid from an array of strings.

    Args:
        strings (list): List of strings to arrange in grid
        width (int): Maximum width of the grid in characters
        padding (int): Padding around each cell (default: 1)

    Returns:
        str: Formatted grid as a string
    """
    if not strings:
        return ""

    max_string_len = max(len(s) for s in strings) if strings else 0
    cell_width = max_string_len + (padding * 2)

    available_width = width - 2  # subtract left and right borders
    n_cols = max(1, available_width // (cell_width + 1))

    n_rows = (len(strings) + n_cols - 1) // n_cols  # ceiling division

    total_border_width = n_cols + 1
    available_cell_width = (width - total_border_width) // n_cols
    cell_width = max(max_string_len, available_cell_width - (padding * 2))

    grid_lines = []

    grid_lines.append("┌" + "─" * (width - 2) + "┐")

    for row in range(n_rows):
        content_line = "│"
        padding_line = "│"

        for col in range(n_cols):
            index = row * n_cols + col
            if index < len(strings):
                text = strings[index]
                left_pad = (cell_width - len(text)) // 2
                right_pad = cell_width - len(text) - left_pad
                content_line += " " * padding + " " * left_pad + \
                    text + " " * right_pad + " " * padding + "│"
                padding_line += " " * (cell_width + padding * 2) + "│"
            else:
                content_line += " " * (cell_width + padding * 2) + "│"
                padding_line += " " * (cell_width + padding * 2) + "│"

        if row == 0:
            grid_lines.append(padding_line)

        grid_lines.append(content_line)

        grid_lines.append(padding_line)

    grid_lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(grid_lines)


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


def paint_bg(text, color):
    return f"{color}{text}{Style.RESET_ALL}"
