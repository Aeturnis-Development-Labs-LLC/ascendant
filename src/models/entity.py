"""Entity base class for all game entities."""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from ..enums import EntityType


class Entity(ABC):
    """Abstract base class for all game entities."""

    def __init__(
        self,
        position: Tuple[int, int],
        entity_type: EntityType,
        entity_id: Optional[str] = None,
    ):
        """Initialize an entity with position and type.

        Args:
            position: Immutable (x, y) position tuple
            entity_type: Type of entity from EntityType enum
            entity_id: Optional unique identifier, auto-generated if not provided
        """
        self._position: Tuple[int, int] = position
        self._entity_type: EntityType = entity_type
        self._entity_id: str = entity_id or str(uuid.uuid4())

    @property
    def position(self) -> Tuple[int, int]:
        """Get the immutable position of this entity."""
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
    def entity_id(self) -> str:
        """Get the unique identifier of this entity."""
        return self._entity_id

    @property
    def entity_type(self) -> EntityType:
        """Get the type of this entity."""
        return self._entity_type

    @abstractmethod
    def update(self) -> None:
        """Update the entity's state.

        This method must be implemented by all subclasses.
        """
        pass

    @abstractmethod
    def render(self) -> str:
        """Render the entity as a string representation.

        This method must be implemented by all subclasses.

        Returns:
            String representation of the entity for display
        """
        pass

    def __str__(self) -> str:
        """Return string representation of the entity."""
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Return detailed representation of the entity."""
        return (
            f"{self.__class__.__name__}(position={self.position}, "
            f"type={self.entity_type}, id={self.entity_id[:8]}...)"
        )
