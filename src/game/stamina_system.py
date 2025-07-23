"""Simple stamina functions for managing character energy."""

from src.enums import ActionType

# Re-export ActionType for convenience
__all__ = [
    "use_stamina",
    "regenerate_stamina",
    "get_action_cost",
    "can_perform_action",
    "ActionType",
]

# Action cost definitions
ACTION_COSTS = {
    ActionType.MOVE: 10,
    ActionType.ATTACK: 15,
    ActionType.USE_ITEM: 10,
    ActionType.WAIT: -20,  # Negative = regeneration
}


def use_stamina(character, amount):
    """Use stamina if available.

    Args:
        character: Character object with stamina attribute
        amount: Amount of stamina to use (int) or ActionType enum

    Returns:
        True if stamina was used, False if insufficient
    """
    # If amount is an ActionType, get its cost
    if isinstance(amount, ActionType):
        amount = get_action_cost(amount)

    # Handle regeneration (negative costs)
    if amount < 0:
        regenerate_stamina(character, -amount)
        return True

    if character.stamina >= amount:
        character.stamina -= amount
        return True
    return False


def regenerate_stamina(character, amount=5):
    """Regenerate stamina up to maximum.

    Args:
        character: Character object with stamina attribute
        amount: Amount to regenerate (default 5)
    """
    character.stamina = min(character.stamina_max, character.stamina + amount)


def get_action_cost(action_type):
    """Get stamina cost for an action type.

    Args:
        action_type: ActionType enum value

    Returns:
        Stamina cost (positive uses stamina, negative regenerates)
    """
    return ACTION_COSTS.get(action_type, 0)


def can_perform_action(character, action_type):
    """Check if character has enough stamina for action.

    Args:
        character: Character to check
        action_type: Action to perform

    Returns:
        True if action can be performed
    """
    cost = get_action_cost(action_type)
    # Regeneration actions always allowed
    if cost <= 0:
        return True
    return character.stamina >= cost
