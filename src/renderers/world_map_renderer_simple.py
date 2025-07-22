"""Simple world map rendering functions."""

from typing import Optional, Tuple

from src.enums import TerrainType
from src.game.environmental_hazards import Weather

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


def render_area(
    world,
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

    # Add weather header
    if current_weather:
        lines.append(f"Weather: {WEATHER_DISPLAY.get(current_weather, 'Unknown')}")
        lines.append("")

    # Render the map area
    for dy in range(-radius, radius + 1):
        line = []
        for dx in range(-radius, radius + 1):
            x, y = center_x + dx, center_y + dy

            # Mark center position with @
            if dx == 0 and dy == 0:
                line.append("@")
                continue

            # Check if position has a location
            location = None
            for loc in world.locations:
                if loc.x == x and loc.y == y:
                    location = loc
                    break

            if location:
                # Show location with special marker
                if location.discovered:
                    line.append("*")
                else:
                    line.append("?")
            else:
                # Show terrain
                if 0 <= x < world.width and 0 <= y < world.height:
                    terrain = world.get_terrain(x, y)
                    char = TERRAIN_CHARS.get(terrain, ".")
                    line.append(char)
                else:
                    line.append(" ")

        lines.append("".join(line))

    # Add legend at bottom
    lines.append("")
    lines.append("Legend: @ You, * Location, ? Unknown, . Plains, F Forest")
    lines.append("        ^ Mountains, ~ Water, = Roads, # Shadowlands")

    return "\n".join(lines)