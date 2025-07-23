"""Default abilities for player characters.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.3 Player Combat Integration
"""

from typing import TYPE_CHECKING, Dict

from src.models.ability import Ability

if TYPE_CHECKING:
    from src.models.character import Character


def get_default_abilities() -> Dict[str, Ability]:
    """Get the default set of abilities for a new character.

    Returns:
        Dictionary of ability name to Ability instance
    """
    return {
        "Power Strike": Ability(
            name="Power Strike",
            description="A powerful attack that deals double damage",
            cooldown_duration=3,
            stamina_cost=20,
            damage_multiplier=2.0,
        ),
        "Quick Attack": Ability(
            name="Quick Attack",
            description="A fast attack with no cooldown but less damage",
            cooldown_duration=0,
            stamina_cost=5,
            damage_multiplier=0.75,
        ),
        "Heavy Slam": Ability(
            name="Heavy Slam",
            description="A devastating attack with high damage and cooldown",
            cooldown_duration=5,
            stamina_cost=30,
            damage_multiplier=3.0,
        ),
        "Precise Strike": Ability(
            name="Precise Strike",
            description="A careful attack with increased critical chance",
            cooldown_duration=2,
            stamina_cost=15,
            damage_multiplier=1.5,
            # TODO: Add crit chance bonus when implementing effect
        ),
        "Defensive Strike": Ability(
            name="Defensive Strike",
            description="Attack while maintaining defense",
            cooldown_duration=1,
            stamina_cost=10,
            damage_multiplier=1.0,
            # TODO: Add defense bonus effect
        ),
    }


def initialize_character_abilities(character: "Character") -> None:
    """Initialize a character with default abilities.

    Args:
        character: Character instance to initialize
    """
    character.abilities = get_default_abilities()

    # Initialize all cooldowns to 0 (ready to use)
    character.ability_cooldowns = dict.fromkeys(character.abilities, 0)
