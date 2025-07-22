"""Tests for color scheme system - UTF Contract GAME-COLOR-001."""

import json
import pytest

from src.enums import TileType, EntityType, TerrainType
from src.rendering.color_scheme import ColorScheme, ColorMode


class TestColorScheme:
    """Test ColorScheme functionality."""

    def test_init_with_defaults(self):
        """Test initialization with default color scheme."""
        scheme = ColorScheme()

        # Should have default mappings for all tile types
        assert scheme.get_color(TileType.FLOOR, ColorMode.RGB) is not None
        assert scheme.get_color(TileType.WALL, ColorMode.RGB) is not None
        assert scheme.get_color(TileType.TRAP, ColorMode.RGB) is not None

    def test_rgb_color_format(self):
        """Test RGB color format is correct."""
        scheme = ColorScheme()

        # RGB should be tuple of 3 integers 0-255
        floor_color = scheme.get_color(TileType.FLOOR, ColorMode.RGB)
        assert isinstance(floor_color, tuple)
        assert len(floor_color) == 3
        assert all(isinstance(c, int) and 0 <= c <= 255 for c in floor_color)

    def test_ansi_color_format(self):
        """Test ANSI color format is correct."""
        scheme = ColorScheme()

        # ANSI should be a string
        floor_color = scheme.get_color(TileType.FLOOR, ColorMode.ANSI)
        assert isinstance(floor_color, str)
        assert floor_color.startswith("\033[")
        assert floor_color.endswith("m")

    def test_load_from_file(self, tmp_path):
        """Test loading color scheme from JSON file."""
        # Create test color config
        config = {
            "tiles": {
                "FLOOR": {"rgb": [128, 128, 128], "ansi": "90"},
                "WALL": {"rgb": [255, 255, 255], "ansi": "97"},
                "TRAP": {"rgb": [139, 0, 0], "ansi": "31"},
            },
            "entities": {
                "PLAYER": {"rgb": [0, 255, 0], "ansi": "92"},
                "MONSTER": {"rgb": [255, 0, 0], "ansi": "91"},
            },
            "terrain": {
                "GRASS": {"rgb": [0, 128, 0], "ansi": "32"},
                "WATER": {"rgb": [0, 0, 255], "ansi": "94"},
            },
        }

        # Write to temp file
        config_file = tmp_path / "colors.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        # Load scheme
        scheme = ColorScheme()
        scheme.load_scheme(str(config_file))

        # Verify loaded colors
        assert scheme.get_color(TileType.FLOOR, ColorMode.RGB) == (128, 128, 128)
        assert scheme.get_color(TileType.WALL, ColorMode.ANSI) == "\033[97m"

    def test_invalid_file_path(self):
        """Test handling of invalid file path."""
        scheme = ColorScheme()

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            scheme.load_scheme("nonexistent.json")

    def test_invalid_json_format(self, tmp_path):
        """Test handling of invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("not valid json{")

        scheme = ColorScheme()
        with pytest.raises(json.JSONDecodeError):
            scheme.load_scheme(str(invalid_file))

    def test_missing_color_returns_default(self):
        """Test missing colors return default."""
        scheme = ColorScheme()

        # Should return a default gray color for unknown types
        # We'll need to handle this gracefully
        default_color = scheme.get_color(TileType.STAIRS_UP, ColorMode.RGB)
        assert default_color is not None
        assert isinstance(default_color, tuple)

    def test_validate_color_ranges(self, tmp_path):
        """Test validation of color value ranges."""
        # Create config with invalid values
        config = {"tiles": {"FLOOR": {"rgb": [256, -1, 128], "ansi": "90"}}}  # Invalid RGB

        config_file = tmp_path / "invalid_colors.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        scheme = ColorScheme()
        with pytest.raises(ValueError, match="RGB values must be 0-255"):
            scheme.load_scheme(str(config_file))

    def test_terrain_type_mapping(self):
        """Test terrain types have appropriate colors."""
        scheme = ColorScheme()

        # Different terrain should have different colors
        plains_color = scheme.get_terrain_color(TerrainType.PLAINS, ColorMode.RGB)
        water_color = scheme.get_terrain_color(TerrainType.WATER, ColorMode.RGB)
        mountains_color = scheme.get_terrain_color(TerrainType.MOUNTAINS, ColorMode.RGB)

        assert plains_color != water_color
        assert water_color != mountains_color
        assert plains_color != mountains_color

    def test_entity_type_mapping(self):
        """Test entity types have appropriate colors."""
        scheme = ColorScheme()

        # Player should be distinct from monsters
        player_color = scheme.get_entity_color(EntityType.PLAYER, ColorMode.RGB)
        monster_color = scheme.get_entity_color(EntityType.MONSTER, ColorMode.RGB)

        assert player_color != monster_color

    def test_color_mode_consistency(self):
        """Test colors are consistent between RGB and ANSI modes."""
        scheme = ColorScheme()

        # Should have both RGB and ANSI for each color
        floor_rgb = scheme.get_color(TileType.FLOOR, ColorMode.RGB)
        floor_ansi = scheme.get_color(TileType.FLOOR, ColorMode.ANSI)

        assert floor_rgb is not None
        assert floor_ansi is not None

    def test_default_color_scheme_completeness(self):
        """Test default scheme covers all enum values."""
        scheme = ColorScheme()

        # Check all tile types
        for tile_type in TileType:
            assert scheme.get_color(tile_type, ColorMode.RGB) is not None
            assert scheme.get_color(tile_type, ColorMode.ANSI) is not None

    def test_custom_color_override(self, tmp_path):
        """Test custom colors override defaults."""
        # Create minimal custom config
        config = {"tiles": {"FLOOR": {"rgb": [50, 50, 50], "ansi": "30"}}}

        config_file = tmp_path / "custom.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        scheme = ColorScheme()
        default_floor = scheme.get_color(TileType.FLOOR, ColorMode.RGB)

        scheme.load_scheme(str(config_file))
        custom_floor = scheme.get_color(TileType.FLOOR, ColorMode.RGB)

        assert custom_floor == (50, 50, 50)
        assert custom_floor != default_floor
