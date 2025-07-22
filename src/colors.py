"""Simplified color system for ASCII rendering.

This module consolidates all color functionality into a single file,
following KISS principles to reduce complexity from 921 lines to ~150 lines.
"""

from enum import Enum
from typing import Dict, Tuple

from src.enums import EntityType, TerrainType, TileType

# Simple color definitions - no need for complex nested structures
TILE_COLORS: Dict[TileType, Tuple[int, int, int]] = {
    TileType.FLOOR: (128, 128, 128),  # Gray
    TileType.WALL: (192, 192, 192),  # Light gray
    TileType.STAIRS_UP: (255, 255, 0),  # Yellow
    TileType.STAIRS_DOWN: (255, 165, 0),  # Orange
    TileType.CHEST: (218, 165, 32),  # Gold
    TileType.TRAP: (139, 0, 0),  # Dark red
}

ENTITY_COLORS: Dict[EntityType, Tuple[int, int, int]] = {
    EntityType.PLAYER: (0, 255, 0),  # Green
    EntityType.MONSTER: (255, 0, 0),  # Red
    EntityType.NPC: (0, 191, 255),  # Cyan
}

TERRAIN_COLORS: Dict[TerrainType, Tuple[int, int, int]] = {
    TerrainType.PLAINS: (144, 238, 144),  # Light green
    TerrainType.FOREST: (34, 139, 34),  # Forest green
    TerrainType.MOUNTAINS: (139, 90, 43),  # Brown
    TerrainType.WATER: (0, 0, 255),  # Blue
    TerrainType.ROADS: (160, 160, 160),  # Light gray
    TerrainType.SHADOWLANDS: (64, 0, 64),  # Dark purple
}

# Default color for unknown types
DEFAULT_COLOR = (128, 128, 128)  # Gray


def get_tile_color(tile_type: TileType, visibility: float = 1.0) -> Tuple[int, int, int]:
    """Get color for a tile with visibility applied.

    Args:
        tile_type: The type of tile
        visibility: Visibility level (0.0 to 1.0)

    Returns:
        RGB color tuple
    """
    base_color = TILE_COLORS.get(tile_type, DEFAULT_COLOR)

    # Apply fog of war dimming
    if visibility < 1.0:
        visibility = max(0.15, visibility)  # Minimum visibility
        return tuple(int(c * visibility) for c in base_color)

    return base_color


def get_entity_color(entity_type: EntityType) -> Tuple[int, int, int]:
    """Get color for an entity type.

    Args:
        entity_type: The type of entity

    Returns:
        RGB color tuple
    """
    return ENTITY_COLORS.get(entity_type, DEFAULT_COLOR)


def get_terrain_color(terrain_type: TerrainType) -> Tuple[int, int, int]:
    """Get color for a terrain type.

    Args:
        terrain_type: The type of terrain

    Returns:
        RGB color tuple
    """
    return TERRAIN_COLORS.get(terrain_type, DEFAULT_COLOR)


def to_ansi(color: Tuple[int, int, int]) -> str:
    """Convert RGB color to ANSI escape code.

    Args:
        color: RGB color tuple

    Returns:
        ANSI escape code string
    """
    r, g, b = color
    return f"\033[38;2;{r};{g};{b}m"


def apply_status_tint(color: Tuple[int, int, int], status: str) -> Tuple[int, int, int]:
    """Apply simple status effect tint to a color.

    Args:
        color: Base RGB color
        status: Status effect name (poison, burning, frozen, blessed)

    Returns:
        Tinted RGB color
    """
    r, g, b = color

    if status == "poison":
        # Green tint
        return (int(r * 0.7), min(255, int(g * 1.5)), int(b * 0.7))
    elif status == "burning":
        # Red tint
        return (min(255, int(r * 1.6)), int(g * 0.8), int(b * 0.5))
    elif status == "frozen":
        # Blue tint
        return (int(r * 0.8), int(g * 0.9), min(255, int(b * 1.5)))
    elif status == "blessed":
        # Golden tint
        return (min(255, int(r * 1.4)), min(255, int(g * 1.3)), int(b * 0.8))

    return color


# Simple colorblind filters (30 lines instead of 174)
def apply_deuteranopia(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Apply red-green colorblind filter (green weakness)."""
    r, g, b = color
    return (int(r * 0.625 + g * 0.375), int(g * 0.7 + r * 0.3), b)


def apply_protanopia(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Apply red-green colorblind filter (red weakness)."""
    r, g, b = color
    return (int(r * 0.567 + g * 0.433), int(r * 0.558 + g * 0.442), b)


def apply_tritanopia(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Apply blue-yellow colorblind filter."""
    r, g, b = color
    return (int(r * 0.95 + b * 0.05), g, int(b * 0.433 + g * 0.567))


def apply_high_contrast(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Push colors to extremes for better visibility."""
    # Calculate luminance
    luminance = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])

    # Push dark colors darker, bright colors brighter
    if luminance < 128:
        factor = luminance / 128 * 0.5
        return tuple(int(c * factor) for c in color)
    else:
        factor = (luminance - 128) / 128 * 0.5
        return tuple(int(c + (255 - c) * factor) for c in color)
