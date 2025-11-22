import random
import re
from typing import Dict, Optional, Tuple, List, Any
from .characters.character import Character
from ..core.interface import Interface


class Dice:
    """
    A complete logic system for resolving action checks in the game.
    
    The Dice class uses AI prompts to determine:
    - Whether an action requires a check
    - The difficulty of the check
    - Which character statistic provides the bonus
    
    It then performs the check using normal game logic (dice roll + stat bonus)
    and can optionally modify the action or its outcome based on the result.
    """
    
    def __init__(self, ai: Interface):
        """
        Initialize the Dice class with an AI interface for prompts.
        
        Args:
            ai: Interface object for making AI prompts
        """
        self.ai = ai
    
    async def resolve_action(
        self,
        action: str,
        character: Character,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolve an action check for a character.
        
        This is the main entry point that orchestrates the entire check process:
        1. Determines if the action requires a check (via AI)
        2. If yes, determines difficulty and stat (via AI)
        3. Performs the dice roll with stat bonus
        4. Optionally modifies the action/outcome based on result
        
        Args:
            action: The action string to check
            character: The character performing the action
            context: Optional context information (plot, history, etc.)
        
        Returns:
            Dictionary containing:
            - requires_check: bool - whether a check was needed
            - success: Optional[bool] - None if no check, True/False if check performed
            - roll_result: Optional[int] - the dice roll result
            - difficulty: Optional[int] - the difficulty of the check
            - stat_used: Optional[str] - the stat that was used
            - stat_bonus: Optional[int] - the bonus from the stat
            - modified_action: Optional[str] - the action after modification (if any)
            - outcome_modification: Optional[str] - description of outcome modification
        """
        result = {
            "requires_check": False,
            "success": None,
            "roll_result": None,
            "difficulty": None,
            "stat_used": None,
            "stat_bonus": None,
            "modified_action": None,
            "outcome_modification": None
        }
        
        # Step 1: Determine if action requires a check
        requires_check = await self._determine_if_check_needed(action, character, context)
        result["requires_check"] = requires_check
        
        if not requires_check:
            return result
        
        # Step 2: Determine difficulty and stat
        check_info = await self._determine_check_parameters(action, character, context)
        if not check_info:
            # If AI couldn't determine parameters, default to no check
            result["requires_check"] = False
            return result
        
        difficulty = check_info["difficulty"]
        stat_name = check_info["stat"]
        result["difficulty"] = difficulty
        result["stat_used"] = stat_name
        
        # Step 3: Perform the check
        check_result = self._perform_check(character, stat_name, difficulty)
        result["roll_result"] = check_result["roll"]
        result["stat_bonus"] = check_result["bonus"]
        result["success"] = check_result["success"]
        
        # Step 4: Optionally modify action/outcome
        modification = self._modify_action_outcome(
            action, 
            check_result["success"], 
            check_result["roll"], 
            difficulty,
            character
        )
        result["modified_action"] = modification.get("action")
        result["outcome_modification"] = modification.get("outcome")
        
        return result
    
    async def _determine_if_check_needed(
        self,
        action: str,
        character: Character,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Use AI to determine if an action requires a skill check.
        
        Args:
            action: The action string
            character: The character performing the action
            context: Optional context information
        
        Returns:
            True if a check is needed, False otherwise
        """
        # Get available stats from character
        available_stats = list(character.stats.stats.keys())
        stats_list = ", ".join(available_stats) if available_stats else "none"
        
        # Build context string
        context_str = ""
        if context:
            if "plot" in context:
                context_str += f"\nPlot context: {context['plot']}"
            if "history" in context:
                context_str += f"\nRecent history: {context['history']}"
        
        prompt = f"""You are a game master determining if an action requires a skill check.

Action: "{action}"
Character: {character.name}
Character background: {character.background}
Available stats: {stats_list}
{context_str}

Determine if this action requires a skill check. Some actions are automatic (like talking, 
walking normally, simple tasks) while others require skill (like climbing, persuading, 
picking locks, fighting, etc.).

Respond with ONLY "yes" or "no" (lowercase)."""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.ai.extract_text(messages)
        response_lower = response.lower().strip()
        
        # Check for yes/positive indicators
        if "yes" in response_lower or "requires" in response_lower or "check" in response_lower:
            # Make sure it's not a negative response
            if "no" not in response_lower[:10] and "not" not in response_lower[:10]:
                return True
        
        return False
    
    async def _determine_check_parameters(
        self,
        action: str,
        character: Character,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Use AI to determine the difficulty and which stat to use for a check.
        
        Args:
            action: The action string
            character: The character performing the action
            context: Optional context information
        
        Returns:
            Dictionary with "difficulty" (int) and "stat" (str) keys, or None if failed
        """
        # Get available stats from character
        available_stats = list(character.stats.stats.keys())
        stats_list = ", ".join(available_stats) if available_stats else "none"
        
        # Build context string
        context_str = ""
        if context:
            if "plot" in context:
                context_str += f"\nPlot context: {context['plot']}"
            if "history" in context:
                context_str += f"\nRecent history: {context['history']}"
        
        prompt = f"""You are a game master determining the difficulty and relevant stat for an action check.

Action: "{action}"
Character: {character.name}
Character background: {character.background}
Available stats: {stats_list}
{context_str}

Determine:
1. The difficulty (DC) of this check. Use a scale from 5 (very easy) to 30 (nearly impossible).
   Typical values: 5-10 (easy), 11-15 (moderate), 16-20 (hard), 21-25 (very hard), 26-30 (nearly impossible).
2. Which stat from the available stats should be used for this check.

Respond in this exact format:
DIFFICULTY: [number]
STAT: [stat_name]

Example:
DIFFICULTY: 15
STAT: dexterity"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.ai.extract_text(messages)
        
        # Parse the response
        difficulty_match = re.search(r'DIFFICULTY:\s*(\d+)', response, re.IGNORECASE)
        stat_match = re.search(r'STAT:\s*(\w+)', response, re.IGNORECASE)
        
        if not difficulty_match or not stat_match:
            return None
        
        difficulty = int(difficulty_match.group(1))
        stat_name = stat_match.group(1).lower()
        
        # Validate stat exists
        if stat_name not in character.stats.stats:
            # Try to find a similar stat (case-insensitive)
            for stat in character.stats.stats.keys():
                if stat.lower() == stat_name:
                    stat_name = stat
                    break
            else:
                # If stat not found, use the first available stat as fallback
                if available_stats:
                    stat_name = available_stats[0]
                else:
                    return None
        
        # Clamp difficulty to reasonable range
        difficulty = max(5, min(30, difficulty))
        
        return {
            "difficulty": difficulty,
            "stat": stat_name
        }
    
    def _perform_check(
        self,
        character: Character,
        stat_name: str,
        difficulty: int
    ) -> Dict[str, Any]:
        """
        Perform the actual dice roll check using game logic (not AI).
        
        Uses a d20 roll + stat bonus against difficulty.
        
        Args:
            character: The character performing the check
            stat_name: The name of the stat to use
            difficulty: The difficulty class (DC) to beat
        
        Returns:
            Dictionary with "roll" (int), "bonus" (int), and "success" (bool)
        """
        # Get stat value
        stat_value = character.stats.stats.get(stat_name, 10)
        
        # Get bonus from stats (using the abstract method)
        # Try to call the get_bonus method on the stats instance
        # If it fails or isn't implemented, fall back to standard D&D calculation
        try:
            # The method signature doesn't include self in the abstract class,
            # but concrete implementations should have it
            bonus = character.stats.get_bonus(stat_value)
        except (TypeError, AttributeError, NotImplementedError):
            # Fallback to standard D&D calculation: (stat - 10) // 2
            bonus = (stat_value - 10) // 2
        
        # Roll d20
        roll = random.randint(1, 20)
        
        # Total = roll + bonus
        total = roll + bonus
        
        # Success if total >= difficulty
        success = total >= difficulty
        
        return {
            "roll": roll,
            "bonus": bonus,
            "total": total,
            "success": success
        }
    
    def _modify_action_outcome(
        self,
        action: str,
        success: bool,
        roll: int,
        difficulty: int,
        character: Character
    ) -> Dict[str, Optional[str]]:
        """
        Optionally modify the action or its outcome based on the check result.
        
        This can add flavor text, modify the action description, or adjust outcomes.
        
        Args:
            action: The original action string
            success: Whether the check succeeded
            roll: The dice roll result
            difficulty: The difficulty of the check
            character: The character performing the action
        
        Returns:
            Dictionary with "action" (modified action string) and "outcome" (outcome description)
        """
        result = {
            "action": None,
            "outcome": None
        }
        
        # Determine outcome based on success and roll quality
        if success:
            if roll == 20:
                # Critical success
                result["outcome"] = f"{character.name} succeeds spectacularly! Critical success!"
            elif roll >= 15:
                result["outcome"] = f"{character.name} succeeds with style!"
            else:
                result["outcome"] = f"{character.name} succeeds."
        else:
            if roll == 1:
                # Critical failure
                result["outcome"] = f"{character.name} fails catastrophically! Critical failure!"
            elif roll <= 5:
                result["outcome"] = f"{character.name} fails badly."
            else:
                result["outcome"] = f"{character.name} fails."
        
        # Optionally modify the action based on the result
        # For critical successes/failures, we might want to add emphasis
        if roll == 20 and success:
            result["action"] = f"{action} (CRITICAL SUCCESS)"
        elif roll == 1 and not success:
            result["action"] = f"{action} (CRITICAL FAILURE)"
        
        return result
    
    def get_available_stats(self, character: Character) -> List[str]:
        """
        Get the list of available stats for a character.
        
        Args:
            character: The character to get stats for
        
        Returns:
            List of stat names
        """
        return list(character.stats.stats.keys())
    
    def get_stat_value(self, character: Character, stat_name: str) -> Optional[int]:
        """
        Get the value of a specific stat for a character.
        
        Args:
            character: The character
            stat_name: The name of the stat
        
        Returns:
            The stat value, or None if not found
        """
        return character.stats.stats.get(stat_name)
    
    def get_stat_bonus(self, character: Character, stat_name: str) -> int:
        """
        Get the bonus value for a specific stat.
        
        Args:
            character: The character
            stat_name: The name of the stat
        
        Returns:
            The bonus value (typically (stat - 10) // 2 in D&D style)
        """
        stat_value = character.stats.stats.get(stat_name, 10)
        try:
            return character.stats.get_bonus(stat_value)
        except (TypeError, AttributeError, NotImplementedError):
            # Fallback to standard D&D calculation
            return (stat_value - 10) // 2

