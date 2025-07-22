"""ASCII renderer for displaying floors with fog of war and color support."""

from typing import Tuple, Optional, List

from src.enums import TileType, EntityType
from src.models.floor import Floor
from src.models.character import Character
from src.models.entity import Entity
from src.rendering.color_scheme import ColorScheme, ColorMode
from src.rendering.color_effects import (
    apply_fog_of_war,
    apply_status_effect,
    flash_damage,
    DamageType,
)
from src.rendering.accessibility import (
    AccessibilityConfig,
    ColorblindMode,
    apply_colorblind_filter,
    apply_high_contrast,
)


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

    def __init__(
        self,
        color_enabled: bool = False,
        color_scheme: Optional[ColorScheme] = None,
        color_mode: ColorMode = ColorMode.ANSI,
        accessibility_config: Optional[AccessibilityConfig] = None,
        fog_radius: int = 5,
    ) -> None:
        """Initialize the ASCII renderer.

        Args:
            color_enabled: Whether to enable color output
            color_scheme: Custom color scheme (uses default if None)
            color_mode: RGB or ANSI color mode
            accessibility_config: Accessibility settings
            fog_radius: Default fog of war radius
        """
        self.color_enabled = color_enabled
        self.color_scheme = color_scheme or ColorScheme()
        self.color_mode = color_mode
        self.accessibility_config = accessibility_config or AccessibilityConfig()
        self.fog_radius = fog_radius

    def render(self, floor: Floor, character: Character) -> str:
        """Render a floor with fog of war and optional colors.

        Args:
            floor: The floor to render
            character: The player character

        Returns:
            Multi-line string representation of the floor
        """
        # Override color if in symbol-only mode
        use_color = self.color_enabled and not self.accessibility_config.symbol_only_mode

        lines = []
        player_x, player_y = character.position

        for y in range(floor.height):
            line = []
            for x in range(floor.width):
                # Check visibility
                visibility = self._calculate_visibility((x, y), character.position)

                if visibility == 0.0:
                    # Fog of war
                    char = self.CHAR_MAP["fog"]
                    if use_color:
                        color = self._get_fog_color()
                        line.append(self._apply_color(char, color))
                    else:
                        line.append(char)
                else:
                    # Visible tile
                    tile = floor.get_tile(x, y)

                    # Check for entities first
                    if (x, y) == character.position:
                        char = self.CHAR_MAP["player"]
                        if use_color:
                            color = self._get_entity_color(character, visibility)
                            line.append(self._apply_color(char, color))
                        else:
                            line.append(char)
                    elif tile.occupant:
                        char = self._get_entity_char(tile.occupant)
                        if use_color:
                            color = self._get_entity_color(tile.occupant, visibility)
                            line.append(self._apply_color(char, color))
                        else:
                            line.append(char)
                    else:
                        # Show tile
                        char = self._get_tile_char(tile)
                        if use_color:
                            color = self._get_tile_color(tile, visibility)
                            line.append(self._apply_color(char, color))
                        else:
                            line.append(char)

            lines.append("".join(line))

        return "\n".join(lines)

    def render_damage_flash(
        self, floor: Floor, character: Character, damage_type: DamageType
    ) -> List[str]:
        """Render damage flash animation frames.

        Args:
            floor: The floor to render
            character: The player character
            damage_type: Type of damage for flash effect

        Returns:
            List of rendered frames for animation
        """
        # Get base color for character
        base_color = self.color_scheme.get_entity_color(EntityType.PLAYER, ColorMode.RGB)
        flash_colors = flash_damage(base_color, damage_type)

        frames = []
        for _ in flash_colors:
            # This is a simplified version - in real implementation would need proper override
            frames.append(self.render(floor, character))

        return frames

    def generate_color_legend(self) -> str:
        """Generate a legend showing color mappings.

        Returns:
            Formatted color legend
        """
        if not self.color_enabled:
            return "Colors disabled"

        lines = ["=== Color Legend ==="]

        # Tiles
        lines.append("\nTiles:")
        for tile_type in TileType:
            char = self._get_tile_char_for_type(tile_type)
            color = self.color_scheme.get_color(tile_type, ColorMode.RGB)
            color_str = (
                self._apply_color(char, color)
                if self.color_mode == ColorMode.ANSI
                else f"RGB{color}"
            )
            lines.append(f"  {char} {tile_type.name}: {color_str}")

        # Entities
        lines.append("\nEntities:")
        player_color = self.color_scheme.get_entity_color(EntityType.PLAYER, ColorMode.RGB)
        monster_color = self.color_scheme.get_entity_color(EntityType.MONSTER, ColorMode.RGB)
        lines.append(f"  @ PLAYER: {self._apply_color('@', player_color)}")
        lines.append(f"  M MONSTER: {self._apply_color('M', monster_color)}")

        return "\n".join(lines)

    def get_entity_color(self, entity: Entity) -> Tuple[int, int, int]:
        """Get color for an entity (for testing).

        Args:
            entity: The entity

        Returns:
            RGB color tuple
        """
        base_color = self.color_scheme.get_entity_color(entity.entity_type, ColorMode.RGB)

        # Apply status effects if present
        if hasattr(entity, "status_effects") and entity.status_effects:
            for effect in entity.status_effects:
                base_color = apply_status_effect(base_color, effect)

        return base_color

    def get_tile_color_rgb(self, tile) -> Tuple[int, int, int]:
        """Get RGB color for a tile (for GUI mode).

        Args:
            tile: The tile

        Returns:
            RGB color tuple
        """
        return self.color_scheme.get_color(tile.tile_type, ColorMode.RGB)

    def _calculate_visibility(self, pos: Tuple[int, int], player_pos: Tuple[int, int]) -> float:
        """Calculate visibility of a position from player position.

        Args:
            pos: Position to check
            player_pos: Player position

        Returns:
            Visibility level (0.0 to 1.0)
        """
        x, y = pos
        px, py = player_pos

        dx = abs(x - px)
        dy = abs(y - py)
        distance_squared = dx * dx + dy * dy
        radius_squared = self.fog_radius * self.fog_radius

        if distance_squared > radius_squared:
            return 0.0
        elif distance_squared == 0:
            return 1.0
        else:
            # Gradual falloff
            distance = distance_squared**0.5
            return 1.0 - (distance / self.fog_radius)

    def _get_tile_char(self, tile) -> str:
        """Get character for a tile."""
        # For now, just return the tile type character
        # TODO: Add trap and chest support when available
        return self.CHAR_MAP.get(tile.tile_type, "?")

    def _get_tile_char_for_type(self, tile_type: TileType) -> str:
        """Get character for a tile type."""
        return self.CHAR_MAP.get(tile_type, "?")

    def _get_entity_char(self, entity: Entity) -> str:
        """Get character for an entity."""
        if entity.entity_type == EntityType.PLAYER:
            return self.CHAR_MAP["player"]
        elif entity.entity_type == EntityType.MONSTER:
            return self.CHAR_MAP["monster"]
        else:
            return "?"

    def _get_tile_color(self, tile, visibility: float) -> Tuple[int, int, int]:
        """Get color for a tile with visibility applied."""
        base_color = self.color_scheme.get_color(tile.tile_type, ColorMode.RGB)

        # Apply fog of war
        color = apply_fog_of_war(base_color, visibility)

        # Apply accessibility filters
        if self.accessibility_config.colorblind_mode != ColorblindMode.NORMAL:
            color = apply_colorblind_filter(color, self.accessibility_config.colorblind_mode)
        if self.accessibility_config.high_contrast_mode:
            color = apply_high_contrast(color)

        return color

    def _get_entity_color(self, entity: Entity, visibility: float) -> Tuple[int, int, int]:
        """Get color for an entity with visibility applied."""
        base_color = self.get_entity_color(entity)

        # Apply fog of war
        color = apply_fog_of_war(base_color, visibility)

        # Apply accessibility filters
        if self.accessibility_config.colorblind_mode != ColorblindMode.NORMAL:
            color = apply_colorblind_filter(color, self.accessibility_config.colorblind_mode)
        if self.accessibility_config.high_contrast_mode:
            color = apply_high_contrast(color)

        return color

    def _get_fog_color(self) -> Tuple[int, int, int]:
        """Get color for fog of war."""
        return (64, 64, 64)  # Dark gray

    def _apply_color(self, char: str, color: Tuple[int, int, int]) -> str:
        """Apply color to a character.

        Args:
            char: Character to color
            color: RGB color tuple

        Returns:
            Colored string (ANSI) or plain char (RGB mode)
        """
        if self.color_mode == ColorMode.ANSI:
            # Convert RGB to ANSI
            r, g, b = color
            # Use 24-bit color ANSI codes
            return f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        else:
            # In RGB mode, just return the char (color handled externally)
            return char

    @staticmethod
    def render_static(floor: Floor, player_pos: Tuple[int, int], vision_radius: int = 5) -> str:
        """Legacy static render method for backward compatibility.

        Args:
            floor: The floor to render
            player_pos: Current player position (x, y)
            vision_radius: How far the player can see

        Returns:
            Multi-line string representation of the floor
        """
        # Legacy rendering that checks floor attributes
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
                    line.append("?")
                else:
                    # Within vision
                    tile = floor.get_tile(x, y)

                    # Check for player first
                    if (x, y) == player_pos:
                        line.append("@")
                    # Check for monsters (legacy attribute)
                    elif hasattr(floor, "monsters") and (x, y) in floor.monsters:
                        line.append("M")
                    # Check for revealed traps (legacy attribute)
                    elif (
                        hasattr(floor, "traps")
                        and (x, y) in floor.traps
                        and floor.traps[(x, y)].get("revealed", False)
                    ):
                        line.append("T")
                    # Check for chests (legacy attribute)
                    elif hasattr(floor, "chests") and (x, y) in floor.chests:
                        line.append("C")
                    # Check stairs
                    elif tile.tile_type == TileType.STAIRS_UP:
                        line.append("^")
                    elif tile.tile_type == TileType.STAIRS_DOWN:
                        line.append("v")
                    elif tile.tile_type == TileType.WALL:
                        line.append("#")
                    elif tile.tile_type == TileType.FLOOR:
                        line.append(".")
                    else:
                        line.append("?")

            lines.append("".join(line))

        return "\n".join(lines)
