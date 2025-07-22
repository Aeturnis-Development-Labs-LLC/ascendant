"""Tests for color accessibility features - UTF Contract GAME-COLOR-003."""

from typing import Tuple

from src.enums import EntityType, TerrainType, TileType
from src.rendering.accessibility import (
    AccessibilityConfig,
    ColorblindMode,
    apply_colorblind_filter,
    apply_high_contrast,
    get_enhanced_symbol,
)


class TestAccessibility:
    """Test accessibility features."""

    def test_colorblind_mode_enum(self):
        """Test ColorblindMode enum has expected values."""
        assert ColorblindMode.NORMAL in ColorblindMode
        assert ColorblindMode.DEUTERANOPIA in ColorblindMode
        assert ColorblindMode.PROTANOPIA in ColorblindMode
        assert ColorblindMode.TRITANOPIA in ColorblindMode

    def test_normal_mode_unchanged(self):
        """Test normal mode doesn't change colors."""
        color = (255, 128, 64)
        result = apply_colorblind_filter(color, ColorblindMode.NORMAL)
        assert result == color

    def test_deuteranopia_filter(self):
        """Test deuteranopia (red-green) colorblind filter."""
        # Pure green should be affected
        green = (0, 255, 0)
        result = apply_colorblind_filter(green, ColorblindMode.DEUTERANOPIA)

        # Green perception should be reduced
        assert result != green
        assert result[1] < green[1]  # Less green

    def test_protanopia_filter(self):
        """Test protanopia (red-green) colorblind filter."""
        # Pure red should be affected
        red = (255, 0, 0)
        result = apply_colorblind_filter(red, ColorblindMode.PROTANOPIA)

        # Red perception should be reduced
        assert result != red
        assert result[0] < red[0]  # Less red

    def test_tritanopia_filter(self):
        """Test tritanopia (blue-yellow) colorblind filter."""
        # Pure blue should be affected
        blue = (0, 0, 255)
        result = apply_colorblind_filter(blue, ColorblindMode.TRITANOPIA)

        # Blue perception should be altered
        assert result != blue

    def test_colorblind_filter_bounds(self):
        """Test colorblind filters respect RGB bounds."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]

        for color in colors:
            for mode in ColorblindMode:
                result = apply_colorblind_filter(color, mode)
                assert all(0 <= c <= 255 for c in result)

    def test_high_contrast_mode(self):
        """Test high contrast mode."""
        # Mid-range color
        color = (128, 128, 128)
        result = apply_high_contrast(color)

        # Should push to extremes
        assert all(c < 64 or c > 192 for c in result)

    def test_high_contrast_preserves_darkness(self):
        """Test high contrast preserves dark colors."""
        dark = (20, 20, 20)
        result = apply_high_contrast(dark)

        # Should be pushed darker
        assert all(c <= dark[i] for i, c in enumerate(result))

    def test_high_contrast_preserves_brightness(self):
        """Test high contrast preserves bright colors."""
        bright = (235, 235, 235)
        result = apply_high_contrast(bright)

        # Should be pushed brighter
        assert all(c >= bright[i] for i, c in enumerate(result))

    def test_symbol_only_mode_tiles(self):
        """Test enhanced symbols for tiles in symbol-only mode."""
        # Each tile type should have distinct symbol
        symbols = set()
        for tile_type in TileType:
            symbol = get_enhanced_symbol(tile_type)
            assert isinstance(symbol, str)
            assert len(symbol) == 1
            symbols.add(symbol)

        # Most symbols should be unique
        assert len(symbols) >= len(TileType) * 0.8

    def test_symbol_only_mode_entities(self):
        """Test enhanced symbols for entities."""
        # Player and monsters should have distinct symbols
        player_symbol = get_enhanced_symbol(EntityType.PLAYER)
        monster_symbol = get_enhanced_symbol(EntityType.MONSTER)

        assert player_symbol != monster_symbol
        assert player_symbol == "@"  # Traditional roguelike

    def test_symbol_only_mode_terrain(self):
        """Test enhanced symbols for terrain."""
        # Different terrain should have different symbols
        plains_symbol = get_enhanced_symbol(TerrainType.PLAINS)
        water_symbol = get_enhanced_symbol(TerrainType.WATER)
        mountains_symbol = get_enhanced_symbol(TerrainType.MOUNTAINS)

        assert plains_symbol != water_symbol
        assert water_symbol != mountains_symbol

    def test_accessibility_config_defaults(self):
        """Test AccessibilityConfig default values."""
        config = AccessibilityConfig()

        assert config.colorblind_mode == ColorblindMode.NORMAL
        assert config.high_contrast_mode is False
        assert config.symbol_only_mode is False

    def test_accessibility_config_toggle(self):
        """Test toggling accessibility features."""
        config = AccessibilityConfig()

        # Toggle high contrast
        config.toggle_high_contrast()
        assert config.high_contrast_mode is True
        config.toggle_high_contrast()
        assert config.high_contrast_mode is False

        # Toggle symbol only
        config.toggle_symbol_only()
        assert config.symbol_only_mode is True

    def test_accessibility_config_cycle_colorblind(self):
        """Test cycling through colorblind modes."""
        config = AccessibilityConfig()

        # Should cycle through all modes
        modes_seen = set()
        for _ in range(10):  # Cycle enough times
            modes_seen.add(config.colorblind_mode)
            config.cycle_colorblind_mode()

        assert len(modes_seen) == len(ColorblindMode)

    def test_apply_all_accessibility_filters(self):
        """Test applying multiple accessibility filters."""
        config = AccessibilityConfig(
            colorblind_mode=ColorblindMode.DEUTERANOPIA,
            high_contrast_mode=True,
            symbol_only_mode=False,
        )

        color = (128, 255, 64)

        # Apply colorblind filter
        result = apply_colorblind_filter(color, config.colorblind_mode)
        # Then high contrast
        result = apply_high_contrast(result)

        # Should be modified by both
        assert result != color
        assert all(0 <= c <= 255 for c in result)

    def test_symbol_consistency(self):
        """Test symbols are consistent."""
        # Same tile type should always give same symbol
        symbol1 = get_enhanced_symbol(TileType.WALL)
        symbol2 = get_enhanced_symbol(TileType.WALL)

        assert symbol1 == symbol2

    def test_important_tiles_have_distinct_symbols(self):
        """Test important tiles have easily distinguishable symbols."""
        # Critical gameplay elements
        wall = get_enhanced_symbol(TileType.WALL)
        floor = get_enhanced_symbol(TileType.FLOOR)
        trap = get_enhanced_symbol(TileType.TRAP)
        stairs_up = get_enhanced_symbol(TileType.STAIRS_UP)
        stairs_down = get_enhanced_symbol(TileType.STAIRS_DOWN)

        # All should be different
        symbols = {wall, floor, trap, stairs_up, stairs_down}
        assert len(symbols) == 5

    def test_colorblind_simulation_accuracy(self):
        """Test colorblind filters approximate real perception."""
        # Red and green should be less distinguishable in deuteranopia
        red = (255, 0, 0)
        green = (0, 255, 0)

        red_filtered = apply_colorblind_filter(red, ColorblindMode.DEUTERANOPIA)
        green_filtered = apply_colorblind_filter(green, ColorblindMode.DEUTERANOPIA)

        # Calculate color distance
        def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
            return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

        original_distance = color_distance(red, green)
        filtered_distance = color_distance(red_filtered, green_filtered)

        # Filtered colors should be closer together
        assert filtered_distance < original_distance
