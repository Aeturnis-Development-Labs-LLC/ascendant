"""Tile data structure for game map positions."""

from typing import TYPE_CHECKING, Optional, Tuple

from ..enums import TileType

if TYPE_CHECKING:
    from .entity import Entity
    from .item import Item


class Tile:
    """Represents a single position on the game map."""

    def __init__(self, x: int, y: int, tile_type: TileType):
        """Initialize a tile with immutable position and type.

        Args:
            x: X coordinate of the tile
            y: Y coordinate of the tile
            tile_type: Type of tile from TileType enum
        """
        self._position: Tuple[int, int] = (x, y)
        self._tile_type: TileType = tile_type
        self._occupant: Optional["Entity"] = None
        self._item: Optional["Item"] = None

    @property
    def position(self) -> Tuple[int, int]:
        """Get the immutable position of this tile."""
        return self._position

    @property
    def x(self) -> int:
        """Get the X coordinate."""
        return self._position[0]

    @property
    def y(self) -> int:
        """Get the Y coordinate."""
        return self._position[1]

    @property
    def tile_type(self) -> TileType:
        """Get the type of this tile."""
        return self._tile_type

    @tile_type.setter
    def tile_type(self, value: TileType) -> None:
        """Set the tile type."""
        self._tile_type = value

    @property
    def occupant(self) -> Optional["Entity"]:
        """Get the entity occupying this tile."""
        return self._occupant

    @occupant.setter
    def occupant(self, entity: Optional["Entity"]) -> None:
        """Set the entity occupying this tile.

        Args:
            entity: Entity to place on this tile, or None to clear

        Raises:
            ValueError: If tile is already occupied by another entity
        """
        if entity is not None and self._occupant is not None:
            raise ValueError(f"Tile at {self.position} is already occupied by {self._occupant}")
        self._occupant = entity

    @property
    def entity(self) -> Optional["Entity"]:
        """Alias for occupant to match expected interface."""
        return self._occupant

    @entity.setter
    def entity(self, entity: Optional["Entity"]) -> None:
        """Alias for occupant setter to match expected interface."""
        self.occupant = entity

    @property
    def item(self) -> Optional["Item"]:
        """Get the item on this tile."""
        return self._item

    @item.setter
    def item(self, item: Optional["Item"]) -> None:
        """Set the item on this tile."""
        self._item = item

    @property
    def is_walkable(self) -> bool:
        """Check if this tile can be walked on.

        Returns:
            True if the tile is FLOOR or STAIRS_UP, False otherwise
        """
        return self._tile_type in (TileType.FLOOR, TileType.STAIRS_UP)

    def is_occupied(self) -> bool:
        """Check if this tile has an entity occupying it.

        Returns:
            True if an entity is on this tile, False otherwise
        """
        return self._occupant is not None

    def __str__(self) -> str:
        """Return string representation of the tile."""
        return f"Tile({self.x}, {self.y}, {self.tile_type})"

    def __repr__(self) -> str:
        """Return detailed representation of the tile."""
        return (
            f"Tile(x={self.x}, y={self.y}, type={self.tile_type}, "
            f"occupied={self._occupant is not None}, has_item={self._item is not None})"
        )
