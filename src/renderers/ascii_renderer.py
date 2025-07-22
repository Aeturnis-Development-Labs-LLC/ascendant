"""ASCII renderer for displaying floors with fog of war."""

from typing import Tuple

from src.enums import TileType
from src.models.floor import Floor


class ASCIIRenderer:
    """Renders floors in ASCII format with fog of war support."""

    # Character mappings for display
    CHAR_MAP = {
        TileType.WALL: "#",
        TileType.FLOOR: ".",
        TileType.STAIRS_UP: "^",
        TileType.STAIRS_DOWN: "v",
        "player": "@",
        "monster": "M",
        "trap": "T",
        "chest": "C",
        "fog": "?",
    }

    @staticmethod
    def render(floor: Floor, player_pos: Tuple[int, int], vision_radius: int = 5) -> str:
        """Render a floor with fog of war based on player position.

        Args:
            floor: The floor to render
            player_pos: Current player position (x, y)
            vision_radius: How far the player can see

        Returns:
            Multi-line string representation of the floor
        """
        lines = []
        player_x, player_y = player_pos

        for y in range(floor.height):
            line = []
            for x in range(floor.width):
                # Check if this position is within vision radius
                dx = abs(x - player_x)
                dy = abs(y - player_y)
                distance_squared = dx * dx + dy * dy
                vision_radius_squared = vision_radius * vision_radius

                if distance_squared > vision_radius_squared:
                    # Outside vision - fog of war
                    line.append(ASCIIRenderer.CHAR_MAP["fog"])
                elif (x, y) == player_pos:
                    # Player position
                    line.append(ASCIIRenderer.CHAR_MAP["player"])
                else:
                    # Visible tile - check what's there
                    tile = floor.get_tile(x, y)

                    # Check for entities first (they override tile display)
                    if hasattr(floor, "monsters") and (x, y) in floor.monsters:
                        line.append(ASCIIRenderer.CHAR_MAP["monster"])
                    elif hasattr(floor, "traps") and (x, y) in floor.traps:
                        # Only show trap if it's been revealed
                        if floor.traps[(x, y)].get("revealed", False):
                            line.append(ASCIIRenderer.CHAR_MAP["trap"])
                        elif tile:
                            line.append(ASCIIRenderer.CHAR_MAP[tile.tile_type])
                        else:
                            line.append(ASCIIRenderer.CHAR_MAP["fog"])
                    elif hasattr(floor, "chests") and (x, y) in floor.chests:
                        line.append(ASCIIRenderer.CHAR_MAP["chest"])
                    elif tile:
                        # Just show the tile type
                        line.append(ASCIIRenderer.CHAR_MAP[tile.tile_type])
                    else:
                        line.append(ASCIIRenderer.CHAR_MAP["fog"])

            lines.append("".join(line))

        return "\n".join(lines)
