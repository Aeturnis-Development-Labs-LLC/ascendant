"""Color effects for dynamic rendering - UTF Contract GAME-COLOR-002."""

from enum import Enum
from typing import List, Tuple


class StatusEffect(Enum):
    """Status effects that modify colors."""

    POISON = "poison"
    BURNING = "burning"
    FROZEN = "frozen"
    CONFUSED = "confused"
    BLESSED = "blessed"


class DamageType(Enum):
    """Damage types for flash effects."""

    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"


def apply_fog_of_war(color: Tuple[int, int, int], visibility: float) -> Tuple[int, int, int]:
    """Apply fog of war dimming to a color.

    Args:
        color: RGB color tuple
        visibility: Visibility level (0.0 = no visibility, 1.0 = full visibility)

    Returns:
        Dimmed RGB color
    """
    # Clamp visibility
    visibility = max(0.0, min(1.0, visibility))

    # Apply visibility as brightness multiplier
    # Add minimum brightness to keep some visibility
    min_brightness = 0.15
    brightness = min_brightness + (1.0 - min_brightness) * visibility

    r, g, b = color
    return (int(r * brightness), int(g * brightness), int(b * brightness))


def apply_status_effect(color: Tuple[int, int, int], effect: StatusEffect) -> Tuple[int, int, int]:
    """Apply status effect tint to a color.

    Args:
        color: RGB color tuple
        effect: Status effect to apply

    Returns:
        Tinted RGB color
    """
    r, g, b = color

    if effect == StatusEffect.POISON:
        # Green tint
        g = min(255, int(g * 1.5))
        r = int(r * 0.7)
        b = int(b * 0.7)

    elif effect == StatusEffect.BURNING:
        # Red/orange tint
        r = min(255, int(r * 1.6))
        g = int(g * 0.8)
        b = int(b * 0.5)

    elif effect == StatusEffect.FROZEN:
        # Blue tint
        b = min(255, int(b * 1.5))
        r = int(r * 0.8)
        g = int(g * 0.9)

    elif effect == StatusEffect.CONFUSED:
        # Purple tint (red + blue)
        r = min(255, int(r * 1.2))
        b = min(255, int(b * 1.2))
        g = int(g * 0.7)

    elif effect == StatusEffect.BLESSED:
        # Golden tint
        r = min(255, int(r * 1.4))
        g = min(255, int(g * 1.3))
        b = int(b * 0.8)

    return (r, g, b)


def flash_damage(
    color: Tuple[int, int, int], damage_type: DamageType
) -> List[Tuple[int, int, int]]:
    """Generate flash animation frames for damage.

    Args:
        color: Base RGB color
        damage_type: Type of damage

    Returns:
        List of RGB colors for animation frames
    """
    frames = []

    if damage_type == DamageType.PHYSICAL:
        # White flash
        frames.append((255, 255, 255))
        frames.append((220, 220, 220))

    elif damage_type == DamageType.FIRE:
        # Red/orange flash
        frames.append((255, 128, 0))
        frames.append((255, 64, 0))

    elif damage_type == DamageType.ICE:
        # Blue/white flash
        frames.append((200, 200, 255))
        frames.append((150, 150, 255))

    elif damage_type == DamageType.POISON:
        # Green flash
        frames.append((0, 255, 0))
        frames.append((0, 200, 0))

    # Return to original
    frames.append(color)

    return frames


def brightness_adjust(color: Tuple[int, int, int], percent: int) -> Tuple[int, int, int]:
    """Adjust brightness of a color.

    Args:
        color: RGB color tuple
        percent: Percentage to adjust (-100 to 100)

    Returns:
        Adjusted RGB color
    """
    # Clamp percent
    percent = max(-100, min(100, percent))

    # Use multiplicative adjustment to maintain ratios better
    factor = 1.0 + (percent / 100.0)

    # Apply factor to all components
    r, g, b = color
    new_r = int(r * factor)
    new_g = int(g * factor)
    new_b = int(b * factor)

    # Clamp to valid range
    return (max(0, min(255, new_r)), max(0, min(255, new_g)), max(0, min(255, new_b)))
