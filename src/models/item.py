"""Item base class for all game items."""

import uuid
from typing import Optional

from ..enums import ItemType


class Item:
    """Base class for all game items."""

    def __init__(
        self,
        name: str,
        item_type: ItemType,
        item_id: Optional[str] = None,
    ):
        """Initialize an item with name and type.

        Args:
            name: Name of the item (must be non-empty)
            item_type: Type of item from ItemType enum
            item_id: Optional unique identifier, auto-generated if not provided

        Raises:
            ValueError: If name is empty or only whitespace
        """
        if not name or not name.strip():
            raise ValueError("Item name cannot be empty")

        self._name: str = name.strip()
        self._item_type: ItemType = item_type
        self._item_id: str = item_id or str(uuid.uuid4())

    @property
    def item_id(self) -> str:
        """Get the unique identifier of this item."""
        return self._item_id

    @property
    def name(self) -> str:
        """Get the name of this item."""
        return self._name

    @property
    def item_type(self) -> ItemType:
        """Get the type of this item."""
        return self._item_type

    def __str__(self) -> str:
        """Return string representation of the item."""
        return f"{self.name} ({self.item_type})"

    def __repr__(self) -> str:
        """Return detailed representation of the item."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', "
            f"type={self.item_type}, id={self.item_id[:8]}...)"
        )
