"""ASCII renderer for world map with weather display."""

from typing import Optional, Tuple

from src.enums import TerrainType
from src.game.environmental_hazards import Weather
from src.models.world_map import WorldMap


class WorldMapRenderer:
    """Renders world map in ASCII format with weather indicators."""

    # Simple terrain display characters
    TERRAIN_CHARS = {
        TerrainType.PLAINS: ".",
        TerrainType.FOREST: "F",
        TerrainType.MOUNTAINS: "^",
        TerrainType.WATER: "~",
        TerrainType.ROADS: "=",
        TerrainType.SHADOWLANDS: "#",
    }

    # Weather display strings
    WEATHER_DISPLAY = {
        Weather.CLEAR: "Clear Skies",
        Weather.FOG: "Foggy (Vision -50%)",
        Weather.STORM: "Stormy (Move -50%)",
        Weather.BLIZZARD: "Blizzard! (Move -70%, Vision -70%)",
    }

    @staticmethod
    def render_area(
        world: WorldMap,
        center: Tuple[int, int],
        radius: int = 10,
        current_weather: Optional[Weather] = None,
    ) -> str:
        """Render a portion of the world map centered on position.

        Args:
            world: The world map to render
            center: Center position (x, y)
            radius: How many tiles to show in each direction
            current_weather: Current weather condition

        Returns:
            Multi-line string with map and weather
        """
        lines = []
        center_x, center_y = center

        # Add weather status at top
        if current_weather:
            weather_text = WorldMapRenderer.WEATHER_DISPLAY.get(current_weather, "Unknown Weather")
            lines.append(f"Weather: {weather_text}")
            lines.append("-" * (len(weather_text) + 9))

        # Render map area
        for dy in range(-radius, radius + 1):
            line = []
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy

                # Mark center with @
                if dx == 0 and dy == 0:
                    line.append("@")
                elif world.is_valid_position(x, y):
                    tile = world.get_tile(x, y)
                    if tile and tile.discovered:
                        # Show location symbols if present
                        if tile.location:
                            line.append(tile.location.get_display_symbol()[1])  # Middle char
                        else:
                            char = WorldMapRenderer.TERRAIN_CHARS.get(tile.terrain_type, "?")
                            line.append(char)
                    else:
                        line.append(" ")  # Undiscovered
                else:
                    line.append(" ")  # Out of bounds

            lines.append("".join(line))

        return "\n".join(lines)
