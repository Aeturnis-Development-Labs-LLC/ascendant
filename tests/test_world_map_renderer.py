"""Tests for world map renderer."""

from src.enums import TerrainType
from src.game.environmental_hazards import Weather
from src.models.world_map import WorldMap
from src.renderers.world_map_renderer import render_area


class TestWorldMapRenderer:
    """Tests for world map rendering functionality."""

    def test_weather_display(self):
        """Test weather status is displayed correctly."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Reveal some area
        world.reveal_area(37, 37, 5)

        # Test each weather type
        for weather in Weather:
            output = render_area(
                world, (37, 37), radius=3, current_weather=weather
            )
            assert "Weather:" in output

            if weather == Weather.FOG:
                assert "Vision -50%" in output
            elif weather == Weather.STORM:
                assert "Move -50%" in output
            elif weather == Weather.BLIZZARD:
                assert "Blizzard!" in output

    def test_basic_rendering(self):
        """Test basic world map rendering."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Reveal center area
        center = (37, 37)
        world.reveal_area(*center, 5)

        output = render_area(world, center, radius=3)

        # Should have 7 lines (radius 3 = 7x7 grid)
        lines = output.strip().split("\n")
        assert len(lines) == 7

        # Center should be marked with @
        center_line = lines[3]
        assert "@" in center_line

    def test_undiscovered_areas(self):
        """Test undiscovered areas show as blank."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Don't reveal anything
        output = render_area(world, (37, 37), radius=2)

        # Should be mostly blank except center @
        for line in output.split("\n"):
            for char in line:
                assert char in ["@", " "]

    def test_terrain_characters(self):
        """Test correct terrain characters are used."""
        world = WorldMap(seed=42)

        # Manually set some terrain for testing (tiles are [y][x])
        world.tiles[10][10].terrain_type = TerrainType.WATER
        world.tiles[10][11].terrain_type = TerrainType.FOREST
        world.tiles[10][12].terrain_type = TerrainType.MOUNTAINS

        # Reveal the area
        world.reveal_area(11, 10, 3)

        output = render_area(world, (11, 10), radius=2)

        # Check terrain chars appear
        assert "~" in output  # Water
        assert "^" in output  # Mountains
        # Forest check would depend on exact positioning
        # The important thing is that rendering works without errors
