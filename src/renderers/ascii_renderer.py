"""Simplified ASCII renderer using KISS color system."""

from typing import List, Optional, Tuple

from src.colors import (
    apply_deuteranopia,
    apply_high_contrast,
    apply_protanopia,
    apply_status_tint,
    apply_tritanopia,
    get_entity_color,
    get_tile_color,
    to_ansi,
)
from src.enums import EntityType, TileType
from src.models.character import Character

# Entity base class removed - checking type directly
from src.models.floor import Floor


class ASCIIRenderer:
    """Renders floors in ASCII format with fog of war and color support."""

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

    @classmethod
    def render_static(
        cls, floor: "Floor", player_pos: Tuple[int, int], vision_radius: int = 5
    ) -> str:
        """Static method for backward compatibility with tests.

        Args:
            floor: The floor to render
            player_pos: Player position for fog of war
            vision_radius: Radius of visibility

        Returns:
            ASCII representation of the floor
        """
        renderer = cls(color_enabled=False, fog_radius=vision_radius)
        return renderer.render(floor, player_pos)

    def __init__(
        self,
        color_enabled: bool = False,
        fog_radius: int = 5,
        colorblind_mode: Optional[str] = None,
        high_contrast: bool = False,
    ) -> None:
        """Initialize the ASCII renderer.

        Args:
            color_enabled: Whether to enable color output
            fog_radius: Radius of fog of war visibility
            colorblind_mode: Optional colorblind filter ('deuteranopia', 'protanopia', 'tritanopia')
            high_contrast: Whether to enable high contrast mode
        """
        self.color_enabled = color_enabled
        self.fog_radius = fog_radius
        self.colorblind_mode = colorblind_mode
        self.high_contrast = high_contrast

    def render(self, floor: Floor, player_pos: Optional[Tuple[int, int]] = None) -> str:
        """Render the floor as an ASCII string with fog of war.

        Args:
            floor: The floor to render
            player_pos: Optional player position for fog of war

        Returns:
            ASCII representation of the floor
        """
        lines = []

        for y in range(floor.height):
            line = []
            for x in range(floor.width):
                char, color = self._get_tile_display(floor, x, y, player_pos)

                if self.color_enabled and color:
                    # Apply colorblind and contrast filters
                    color = self._apply_accessibility_filters(color)
                    line.append(f"{to_ansi(color)}{char}\033[0m")
                else:
                    line.append(char)

            lines.append("".join(line))

        return "\n".join(lines)

    def _get_tile_display(
        self, floor: Floor, x: int, y: int, player_pos: Optional[Tuple[int, int]]
    ) -> Tuple[str, Optional[Tuple[int, int, int]]]:
        """Get the character and color for a tile position.

        Args:
            floor: The floor being rendered
            x, y: Tile coordinates
            player_pos: Optional player position for fog of war

        Returns:
            Tuple of (character, color)
        """
        # Check if tile is visible (fog of war)
        if player_pos:
            dist_squared = (x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2
            if dist_squared > self.fog_radius**2:
                return self.CHAR_MAP["fog"], (64, 64, 64)  # Dark gray for fog

        # Check if player is at this position
        if player_pos and (x, y) == player_pos:
            return self.CHAR_MAP["player"], (255, 255, 255) if self.color_enabled else None

        # Check for monsters
        if hasattr(floor, "monsters") and (x, y) in floor.monsters:
            return self.CHAR_MAP["monster"], (255, 0, 0) if self.color_enabled else None

        # Check for chests
        if hasattr(floor, "chests") and (x, y) in floor.chests:
            return self.CHAR_MAP["chest"], (255, 215, 0) if self.color_enabled else None

        # Check for traps (only show if revealed)
        if hasattr(floor, "traps") and (x, y) in floor.traps:
            trap_data = floor.traps[(x, y)]
            if trap_data.get("revealed", False):
                return self.CHAR_MAP["trap"], (255, 0, 255) if self.color_enabled else None

        # Check for entities
        if hasattr(floor, "entities"):
            for entity in floor.entities:
                if entity.x == x and entity.y == y:
                    char = self._get_entity_char(entity)
                    color = None
                    if self.color_enabled:
                        color = get_entity_color(entity.entity_type)
                        # Apply status effects if present
                        if hasattr(entity, "status") and entity.status:
                            color = apply_status_tint(color, entity.status)
                    return char, color

        # Get tile from floor.tiles
        if (x, y) in floor.tiles:
            tile = floor.tiles[(x, y)]
            tile_type = tile.tile_type
            char = self.CHAR_MAP.get(tile_type, "?")
            color = None
            if self.color_enabled:
                # Apply fog of war dimming
                visibility = 1.0
                if player_pos:
                    dist_squared = (x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2
                    max_dist_squared = self.fog_radius**2
                    visibility = max(0.3, 1.0 - (dist_squared / max_dist_squared))
                color = get_tile_color(tile_type, visibility)
            return char, color
        else:
            # Empty space
            return " ", None

    def _get_entity_char(self, entity) -> str:
        """Get the display character for an entity."""
        if isinstance(entity, Character):
            return self.CHAR_MAP["player"]
        elif hasattr(entity, "entity_type") and entity.entity_type == EntityType.MONSTER:
            return self.CHAR_MAP["monster"]
        else:
            return "?"

    def _apply_accessibility_filters(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply colorblind and contrast filters to a color."""
        # Apply colorblind filter
        if self.colorblind_mode == "deuteranopia":
            color = apply_deuteranopia(color)
        elif self.colorblind_mode == "protanopia":
            color = apply_protanopia(color)
        elif self.colorblind_mode == "tritanopia":
            color = apply_tritanopia(color)

        # Apply high contrast
        if self.high_contrast:
            color = apply_high_contrast(color)

        return color

    def render_with_info(self, floor: Floor, player_pos: Optional[Tuple[int, int]] = None) -> str:
        """Render the floor with additional information."""
        floor_display = self.render(floor, player_pos)

        info_lines = [
            f"Floor {getattr(floor, 'level', 1)}",
            f"Size: {floor.width}x{floor.height}",
            f"Rooms: {len(floor.rooms)}",
        ]

        if self.color_enabled:
            info_lines.append("Colors: Enabled")
            if self.colorblind_mode:
                info_lines.append(f"Colorblind Mode: {self.colorblind_mode}")
            if self.high_contrast:
                info_lines.append("High Contrast: On")

        return floor_display + "\n\n" + "\n".join(info_lines)
