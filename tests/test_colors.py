"""Tests for the simplified color system."""

import pytest

from src.colors import (
    DEFAULT_COLOR,
    ENTITY_COLORS,
    TERRAIN_COLORS,
    TILE_COLORS,
    apply_deuteranopia,
    apply_high_contrast,
    apply_protanopia,
    apply_status_tint,
    apply_tritanopia,
    get_entity_color,
    get_terrain_color,
    get_tile_color,
    to_ansi,
)
from src.enums import EntityType, TerrainType, TileType


class TestColorFunctions:
    """Test color retrieval and manipulation functions."""

    def test_get_tile_color_known_type(self):
        """Test getting color for known tile types."""
        assert get_tile_color(TileType.FLOOR) == (128, 128, 128)
        assert get_tile_color(TileType.WALL) == (192, 192, 192)
        assert get_tile_color(TileType.STAIRS_UP) == (255, 255, 0)

    def test_get_tile_color_with_visibility(self):
        """Test tile color with fog of war visibility."""
        base_color = TILE_COLORS[TileType.FLOOR]

        # Full visibility
        assert get_tile_color(TileType.FLOOR, 1.0) == base_color

        # Half visibility
        half_visible = get_tile_color(TileType.FLOOR, 0.5)
        assert half_visible == (64, 64, 64)

        # Minimum visibility (0.15)
        min_visible = get_tile_color(TileType.FLOOR, 0.0)
        assert min_visible == (19, 19, 19)  # 128 * 0.15

    def test_get_entity_color(self):
        """Test getting colors for entity types."""
        assert get_entity_color(EntityType.PLAYER) == (0, 255, 0)
        assert get_entity_color(EntityType.MONSTER) == (255, 0, 0)
        assert get_entity_color(EntityType.NPC) == (0, 191, 255)

    def test_get_terrain_color(self):
        """Test getting colors for terrain types."""
        assert get_terrain_color(TerrainType.PLAINS) == (144, 238, 144)
        assert get_terrain_color(TerrainType.FOREST) == (34, 139, 34)
        assert get_terrain_color(TerrainType.WATER) == (0, 0, 255)

    def test_to_ansi(self):
        """Test RGB to ANSI conversion."""
        assert to_ansi((255, 0, 0)) == "\033[38;2;255;0;0m"
        assert to_ansi((0, 255, 0)) == "\033[38;2;0;255;0m"
        assert to_ansi((128, 128, 128)) == "\033[38;2;128;128;128m"

    def test_apply_status_tint(self):
        """Test status effect color tinting."""
        base_color = (100, 100, 100)

        # Poison (green tint)
        poison = apply_status_tint(base_color, "poison")
        assert poison[1] > poison[0]  # More green
        assert poison[1] > poison[2]

        # Burning (red tint)
        burning = apply_status_tint(base_color, "burning")
        assert burning[0] > burning[1]  # More red
        assert burning[0] > burning[2]

        # Frozen (blue tint)
        frozen = apply_status_tint(base_color, "frozen")
        assert frozen[2] > frozen[0]  # More blue
        assert frozen[2] > frozen[1]

        # Blessed (golden tint)
        blessed = apply_status_tint(base_color, "blessed")
        assert blessed[0] > base_color[0]  # More red
        assert blessed[1] > base_color[1]  # More green

        # Unknown status
        assert apply_status_tint(base_color, "unknown") == base_color


class TestColorblindFilters:
    """Test colorblind accessibility filters."""

    def test_apply_deuteranopia(self):
        """Test red-green colorblind filter (green weakness)."""
        # Pure green should be shifted
        green = (0, 255, 0)
        filtered = apply_deuteranopia(green)
        assert filtered[0] > 0  # Some red mixed in
        assert filtered[1] < 255  # Less pure green
        assert filtered[2] == 0  # Blue unchanged

        # Test with mixed color
        color = (100, 150, 200)
        filtered = apply_deuteranopia(color)
        assert filtered[2] == 200  # Blue unchanged

    def test_apply_protanopia(self):
        """Test red-green colorblind filter (red weakness)."""
        # Pure red should be shifted
        red = (255, 0, 0)
        filtered = apply_protanopia(red)
        assert filtered[0] < 255  # Less pure red
        assert filtered[1] > 0  # Some green mixed in
        assert filtered[2] == 0  # Blue unchanged

    def test_apply_tritanopia(self):
        """Test blue-yellow colorblind filter."""
        # Pure blue should be shifted
        blue = (0, 0, 255)
        filtered = apply_tritanopia(blue)
        assert filtered[0] > 0  # Some red mixed in
        assert filtered[1] == 0  # Green unchanged
        assert filtered[2] < 255  # Less pure blue

    def test_apply_high_contrast(self):
        """Test high contrast filter."""
        # Dark color should get darker
        dark = (50, 50, 50)
        filtered = apply_high_contrast(dark)
        assert all(filtered[i] < dark[i] for i in range(3))

        # Bright color should get brighter
        bright = (200, 200, 200)
        filtered = apply_high_contrast(bright)
        assert all(filtered[i] > bright[i] for i in range(3))

        # Mid-tone should also change
        mid = (128, 128, 128)
        filtered = apply_high_contrast(mid)
        # At luminance 128, it should be slightly darker
        assert all(filtered[i] <= mid[i] for i in range(3))
