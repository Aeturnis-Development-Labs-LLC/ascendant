"""Color scheme management for ASCII rendering - UTF Contract GAME-COLOR-001."""

import json
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple, Union

from src.enums import TileType, EntityType, TerrainType


class ColorMode(Enum):
    """Color output modes."""

    RGB = "rgb"
    ANSI = "ansi"


class ColorScheme:
    """Manages color mappings for tiles, entities, and terrain."""

    def __init__(self) -> None:
        """Initialize with default color scheme."""
        self._colors: Dict[str, Dict[str, Union[Tuple[int, int, int], str]]] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default color scheme."""
        # Tile colors
        self._colors["tiles"] = {
            "FLOOR": {"rgb": (128, 128, 128), "ansi": "\033[90m"},  # Dark gray
            "WALL": {"rgb": (192, 192, 192), "ansi": "\033[37m"},  # Light gray
            "STAIRS_UP": {"rgb": (255, 255, 0), "ansi": "\033[93m"},  # Bright yellow
            "STAIRS_DOWN": {"rgb": (255, 165, 0), "ansi": "\033[33m"},  # Orange
            "CHEST": {"rgb": (218, 165, 32), "ansi": "\033[33m"},  # Gold
            "TRAP": {"rgb": (139, 0, 0), "ansi": "\033[31m"},  # Dark red
        }

        # Entity colors
        self._colors["entities"] = {
            "PLAYER": {"rgb": (0, 255, 0), "ansi": "\033[92m"},  # Bright green
            "MONSTER": {"rgb": (255, 0, 0), "ansi": "\033[91m"},  # Bright red
            "NPC": {"rgb": (0, 191, 255), "ansi": "\033[96m"},  # Bright cyan
        }

        # Terrain colors
        self._colors["terrain"] = {
            "PLAINS": {"rgb": (144, 238, 144), "ansi": "\033[92m"},  # Light green
            "FOREST": {"rgb": (34, 139, 34), "ansi": "\033[32m"},  # Forest green
            "MOUNTAINS": {"rgb": (139, 90, 43), "ansi": "\033[33m"},  # Brown
            "WATER": {"rgb": (0, 0, 255), "ansi": "\033[94m"},  # Bright blue
            "ROADS": {"rgb": (160, 160, 160), "ansi": "\033[37m"},  # Light gray
            "SHADOWLANDS": {"rgb": (64, 0, 64), "ansi": "\033[35m"},  # Dark purple
            "DUNGEON_ENTRANCE": {"rgb": (64, 64, 64), "ansi": "\033[90m"},  # Dark gray
            "SAFE_HAVEN": {"rgb": (255, 215, 0), "ansi": "\033[93m"},  # Gold
            "TOWER_ENTRANCE": {"rgb": (148, 0, 211), "ansi": "\033[95m"},  # Purple
        }

        # Default color for unknown types
        self._default_color = {"rgb": (128, 128, 128), "ansi": "\033[90m"}

    def load_scheme(self, file_path: str) -> None:
        """Load color scheme from JSON file.

        Args:
            file_path: Path to JSON color configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If color values are out of range
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Color scheme file not found: {file_path}")

        with open(path, "r") as f:
            config = json.load(f)

        # Validate and merge with existing colors
        for category in ["tiles", "entities", "terrain"]:
            if category in config:
                if category not in self._colors:
                    self._colors[category] = {}

                for key, color_data in config[category].items():
                    if "rgb" in color_data:
                        rgb = color_data["rgb"]
                        if not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
                            raise ValueError(f"RGB values must be 0-255, got {rgb}")
                        color_data["rgb"] = tuple(rgb)

                    if "ansi" in color_data:
                        # Convert simple ANSI codes to full escape sequences
                        ansi = color_data["ansi"]
                        if not ansi.startswith("\033["):
                            color_data["ansi"] = f"\033[{ansi}m"

                    self._colors[category][key] = color_data

    def get_color(self, tile_type: TileType, mode: ColorMode) -> Union[Tuple[int, int, int], str]:
        """Get color for a tile type.

        Args:
            tile_type: The tile type
            mode: RGB or ANSI mode

        Returns:
            RGB tuple or ANSI string
        """
        key = tile_type.name
        if key in self._colors.get("tiles", {}):
            return self._colors["tiles"][key][mode.value]
        return self._default_color[mode.value]

    def get_terrain_color(
        self, terrain_type: TerrainType, mode: ColorMode
    ) -> Union[Tuple[int, int, int], str]:
        """Get color for terrain type.

        Args:
            terrain_type: The terrain type
            mode: RGB or ANSI mode

        Returns:
            RGB tuple or ANSI string
        """
        key = terrain_type.name
        if key in self._colors.get("terrain", {}):
            return self._colors["terrain"][key][mode.value]
        return self._default_color[mode.value]

    def get_entity_color(
        self, entity_type: EntityType, mode: ColorMode
    ) -> Union[Tuple[int, int, int], str]:
        """Get color for entity type.

        Args:
            entity_type: The entity type
            mode: RGB or ANSI mode

        Returns:
            RGB tuple or ANSI string
        """
        key = entity_type.name
        if key in self._colors.get("entities", {}):
            return self._colors["entities"][key][mode.value]
        return self._default_color[mode.value]
