"""Accessibility features for color rendering - UTF Contract GAME-COLOR-003."""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union

from src.enums import TileType, EntityType, TerrainType


class ColorblindMode(Enum):
    """Colorblind simulation modes."""

    NORMAL = "normal"
    DEUTERANOPIA = "deuteranopia"  # Red-green (most common)
    PROTANOPIA = "protanopia"  # Red-green
    TRITANOPIA = "tritanopia"  # Blue-yellow


@dataclass
class AccessibilityConfig:
    """Configuration for accessibility features."""

    colorblind_mode: ColorblindMode = ColorblindMode.NORMAL
    high_contrast_mode: bool = False
    symbol_only_mode: bool = False

    def toggle_high_contrast(self) -> None:
        """Toggle high contrast mode."""
        self.high_contrast_mode = not self.high_contrast_mode

    def toggle_symbol_only(self) -> None:
        """Toggle symbol only mode."""
        self.symbol_only_mode = not self.symbol_only_mode

    def cycle_colorblind_mode(self) -> None:
        """Cycle through colorblind modes."""
        modes = list(ColorblindMode)
        current_index = modes.index(self.colorblind_mode)
        next_index = (current_index + 1) % len(modes)
        self.colorblind_mode = modes[next_index]


def apply_colorblind_filter(
    color: Tuple[int, int, int], mode: ColorblindMode
) -> Tuple[int, int, int]:
    """Apply colorblind simulation filter.

    Args:
        color: RGB color tuple
        mode: Colorblind mode to simulate

    Returns:
        Filtered RGB color
    """
    if mode == ColorblindMode.NORMAL:
        return color

    r, g, b = color

    if mode == ColorblindMode.DEUTERANOPIA:
        # Simulate red-green colorblindness (green weakness)
        # Shift green towards red
        new_r = int(0.625 * r + 0.375 * g)
        new_g = int(0.7 * g + 0.3 * r)
        new_b = b

    elif mode == ColorblindMode.PROTANOPIA:
        # Simulate red-green colorblindness (red weakness)
        # Shift red towards green
        new_r = int(0.567 * r + 0.433 * g)
        new_g = int(0.558 * r + 0.442 * g)
        new_b = b

    elif mode == ColorblindMode.TRITANOPIA:
        # Simulate blue-yellow colorblindness
        # Reduce blue-yellow distinction
        new_r = int(0.95 * r + 0.05 * b)
        new_g = g
        new_b = int(0.433 * b + 0.567 * g)

    else:
        return color

    # Ensure values are in valid range (only reached for colorblind modes)
    return (max(0, min(255, new_r)), max(0, min(255, new_g)), max(0, min(255, new_b)))


def apply_high_contrast(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Apply high contrast adjustment.

    Args:
        color: RGB color tuple

    Returns:
        High contrast RGB color
    """
    # Calculate luminance
    luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

    # Push colors to extremes based on luminance
    if luminance < 128:
        # Dark colors become darker
        factor = luminance / 128
        r, g, b = color
        return (int(r * factor * 0.5), int(g * factor * 0.5), int(b * factor * 0.5))
    else:
        # Bright colors become brighter
        factor = (luminance - 128) / 128
        r, g, b = color
        return (
            int(r + (255 - r) * factor * 0.5),
            int(g + (255 - g) * factor * 0.5),
            int(b + (255 - b) * factor * 0.5),
        )


def get_symbol_for_tile(tile_type: TileType) -> str:
    """Get basic symbol for tile type.

    Args:
        tile_type: The tile type

    Returns:
        Single character symbol
    """
    symbols = {
        TileType.FLOOR: ".",
        TileType.WALL: "#",
        TileType.STAIRS_UP: "<",
        TileType.STAIRS_DOWN: ">",
        TileType.CHEST: "=",
        TileType.TRAP: "^",
    }
    return symbols.get(tile_type, "?")


def get_enhanced_symbol(element: Union[TileType, EntityType, TerrainType]) -> str:
    """Get enhanced symbol for accessibility mode.

    Args:
        element: Tile, entity, or terrain type

    Returns:
        Enhanced single character symbol
    """
    if isinstance(element, TileType):
        # Enhanced tile symbols
        symbols = {
            TileType.FLOOR: "·",  # Middle dot
            TileType.WALL: "█",  # Full block
            TileType.STAIRS_UP: "▲",  # Up triangle
            TileType.STAIRS_DOWN: "▼",  # Down triangle
            TileType.CHEST: "□",  # Box
            TileType.TRAP: "×",  # X mark
        }
        return symbols.get(element, get_symbol_for_tile(element))

    elif isinstance(element, EntityType):
        # Entity symbols
        entity_symbols = {
            EntityType.PLAYER: "@",
            EntityType.MONSTER: "&",
            EntityType.NPC: "☺",  # Smiley
        }
        return entity_symbols.get(element, "?")

    elif isinstance(element, TerrainType):
        # Terrain symbols
        terrain_symbols = {
            TerrainType.PLAINS: '"',
            TerrainType.FOREST: "♣",
            TerrainType.MOUNTAINS: "^",
            TerrainType.WATER: "~",
            TerrainType.ROADS: "=",
            TerrainType.SHADOWLANDS: "░",
        }
        return terrain_symbols.get(element, "?")

    return "?"
