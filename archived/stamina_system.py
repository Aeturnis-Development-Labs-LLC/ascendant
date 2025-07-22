"""Stamina system for managing character energy and actions."""

import random

from src.enums import ActionType
from src.models.character import Character


class StaminaSystem:
    """Manages stamina costs, regeneration, and forced waits."""

    # Action cost definitions
    ACTION_COSTS = {
        ActionType.MOVE: 10,
        ActionType.ATTACK: 15,
        ActionType.USE_ITEM: 10,
        ActionType.CAST_SPELL: -1,  # Variable cost, handled separately
        ActionType.WAIT: -20,  # Negative = regeneration
    }

    # Stamina regeneration per idle turn
    REGENERATION_PER_TURN = 5

    # Minimum stamina to perform basic actions
    MIN_ACTION_STAMINA = 10

    @staticmethod
    def get_action_cost(action_type: ActionType) -> int:
        """Get the stamina cost for an action.

        Args:
            action_type: Type of action to check

        Returns:
            Stamina cost (positive) or regeneration (negative)
        """
        if action_type == ActionType.CAST_SPELL:
            # Variable cost between 20-50
            return random.randint(20, 50)
        return StaminaSystem.ACTION_COSTS.get(action_type, 0)

    @staticmethod
    def can_perform_action(character: Character, action_type: ActionType) -> bool:
        """Check if character has enough stamina for an action.

        Args:
            character: Character to check
            action_type: Action to perform

        Returns:
            True if action can be performed
        """
        cost = StaminaSystem.get_action_cost(action_type)
        # Wait action always allowed (it regenerates)
        if cost < 0:
            return True
        return character.stamina >= cost

    @staticmethod
    def execute_action(character: Character, action_type: ActionType) -> bool:
        """Execute an action, consuming or regenerating stamina.

        Args:
            character: Character performing action
            action_type: Type of action

        Returns:
            True if action was executed
        """
        cost = StaminaSystem.get_action_cost(action_type)

        # Handle regeneration actions (negative cost)
        if cost < 0:
            character.stamina -= cost  # Subtracting negative = adding
            return True

        # Check if action can be performed
        if character.stamina >= cost:
            return character.perform_action(action_type, cost)

        return False

    @staticmethod
    def regenerate(character: Character, turns: int) -> None:
        """Regenerate stamina over idle turns.

        Args:
            character: Character to regenerate
            turns: Number of idle turns
        """
        regen_amount = StaminaSystem.REGENERATION_PER_TURN * turns
        character.stamina += regen_amount

    @staticmethod
    def force_wait_if_exhausted(character: Character) -> bool:
        """Force a wait action if character is too exhausted.

        Args:
            character: Character to check

        Returns:
            True if wait was forced, False otherwise
        """
        if character.stamina < StaminaSystem.MIN_ACTION_STAMINA:
            # Force wait action
            StaminaSystem.execute_action(character, ActionType.WAIT)
            return True
        return False

    @staticmethod
    def get_stamina_percentage(character: Character) -> int:
        """Get stamina as percentage of maximum.

        Args:
            character: Character to check

        Returns:
            Stamina percentage (0-100)
        """
        if character.stamina_max == 0:
            return 0
        return int((character.stamina / character.stamina_max) * 100)

    @staticmethod
    def get_stamina_state(character: Character) -> str:
        """Get descriptive stamina state for UI display.

        Args:
            character: Character to check

        Returns:
            State string: EXHAUSTED, CRITICAL, LOW, MEDIUM, HIGH, FULL
        """
        percentage = StaminaSystem.get_stamina_percentage(character)

        if percentage == 0:
            return "EXHAUSTED"
        elif percentage <= 20:
            return "CRITICAL"
        elif percentage <= 40:
            return "LOW"
        elif percentage <= 60:
            return "MEDIUM"
        elif percentage < 100:
            return "HIGH"
        else:
            return "FULL"
