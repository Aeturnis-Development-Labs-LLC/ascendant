"""Simple entity base class for game entities.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

from abc import ABC, abstractmethod
from typing import Tuple

from src.enums import EntityType


class Entity(ABC):
    """Simple abstract base class for all game entities."""

    def __init__(self, x: int, y: int, entity_type: EntityType):
        """Initialize entity with position and type."""
        self.x = x
        self.y = y
        self.entity_type = entity_type

    @property
    def position(self) -> Tuple[int, int]:
        """Get position as tuple."""
        return (self.x, self.y)

    @abstractmethod
    def render(self) -> str:
        """Return display character for entity."""
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update entity state."""
        pass

    def __str__(self) -> str:
        """String representation of entity."""
        return f"Entity at ({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Developer representation of entity."""
        return f"Entity(x={self.x}, y={self.y}, type={self.entity_type})"
