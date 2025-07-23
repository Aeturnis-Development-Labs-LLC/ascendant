"""Map display widget for rendering the game world."""

from typing import List, Optional, Tuple

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from src.enums import TileType
from src.models.floor import Floor


class MapWidget(QWidget):
    """Widget for displaying the game map with tile-based rendering."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the map widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Game state
        self.floor: Optional[Floor] = None
        self.player_pos: Optional[Tuple[int, int]] = None

        # Display properties
        self.tile_size: int = 20  # Default tile size
        self.colors = {
            "background": QColor("#1a1a1a"),
            "wall": QColor("#666666"),
            "floor": QColor("#333333"),
            "player": QColor("#00ff00"),
            "monster": QColor("#ff0000"),
            "highlight": QColor("#ffff00"),
            "valid_move": QColor("#0066ff"),
        }

        # Visual feedback
        self.hover_tile: Optional[Tuple[int, int]] = None
        self.valid_moves: List[Tuple[int, int]] = []
        self.flashing_tiles: dict[Tuple[int, int], str] = {}

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def set_floor(self, floor: Floor) -> None:
        """Set the floor to display.

        Args:
            floor: Floor object to render
        """
        self.floor = floor
        self._recalculate_tile_size()
        self.update()

    def set_player_position(self, x: int, y: int) -> None:
        """Set the player position.

        Args:
            x: Player X coordinate
            y: Player Y coordinate
        """
        self.player_pos = (x, y)
        self.update()

    def set_valid_moves(self, moves: List[Tuple[int, int]]) -> None:
        """Set the list of valid move positions.

        Args:
            moves: List of (x, y) tuples for valid moves
        """
        self.valid_moves = moves
        self.update()

    def flash_tile(self, x: int, y: int, flash_type: str) -> None:
        """Flash a tile for visual feedback.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            flash_type: Type of flash (e.g., "combat")
        """
        self.flashing_tiles[(x, y)] = flash_type
        self.update()

    def clear_flash(self, x: int, y: int) -> None:
        """Clear flash effect from a tile.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
        """
        if (x, y) in self.flashing_tiles:
            del self.flashing_tiles[(x, y)]
            self.update()

    def paintEvent(self, event: Optional[QPaintEvent]) -> None:
        """Handle paint event to render the map.

        Args:
            event: Paint event (unused)
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Fill background
        painter.fillRect(self.rect(), self.colors["background"])

        # If no floor, nothing more to draw
        if not self.floor:
            painter.end()
            return

        # Calculate viewport
        min_x, max_x, min_y, max_y = self._calculate_viewport()

        # Draw tiles
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if 0 <= x < self.floor.width and 0 <= y < self.floor.height:
                    self._draw_tile(painter, x, y)

        # Draw player
        if self.player_pos:
            x, y = self.player_pos
            if min_x <= x <= max_x and min_y <= y <= max_y:
                self._draw_player(painter, x, y)

        painter.end()

    def _draw_tile(self, painter: QPainter, x: int, y: int) -> None:
        """Draw a single tile.

        Args:
            painter: QPainter instance
            x: Tile X coordinate
            y: Tile Y coordinate
        """
        if not self.floor:
            return
            
        tile = self.floor.get_tile(x, y)
        if not tile:
            return
            
        screen_x, screen_y = self._tile_to_screen(x, y)
        rect = QRect(screen_x, screen_y, self.tile_size, self.tile_size)

        # Determine base color
        if tile.tile_type == TileType.WALL:
            color = self.colors["wall"]
        elif tile.tile_type == TileType.FLOOR:
            color = self.colors["floor"]
        else:
            color = self.colors["floor"]  # Default for other types

        # Apply visual effects
        if (x, y) in self.flashing_tiles:
            # Flash effect - use highlight color
            color = self.colors["highlight"]
        elif (x, y) == self.hover_tile:
            # Hover effect - lighten the color
            color = color.lighter(120)
        elif (x, y) in self.valid_moves:
            # Valid move overlay
            painter.fillRect(rect, color)
            painter.fillRect(rect, QColor(0, 102, 255, 64))  # Semi-transparent blue
            return

        painter.fillRect(rect, color)

    def _draw_player(self, painter: QPainter, x: int, y: int) -> None:
        """Draw the player.

        Args:
            painter: QPainter instance
            x: Player X coordinate
            y: Player Y coordinate
        """
        screen_x, screen_y = self._tile_to_screen(x, y)

        # Draw player as a filled circle
        painter.setBrush(QBrush(self.colors["player"]))
        painter.setPen(Qt.PenStyle.NoPen)

        # Center the circle in the tile
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        radius = self.tile_size // 3

        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)

    def _calculate_viewport(self) -> Tuple[int, int, int, int]:
        """Calculate the visible viewport in tile coordinates.

        Returns:
            Tuple of (min_x, max_x, min_y, max_y)
        """
        if not self.floor:
            return (0, 0, 0, 0)

        # Calculate how many tiles fit on screen
        tiles_x = self.width() // self.tile_size
        tiles_y = self.height() // self.tile_size

        # Center on player if possible
        if self.player_pos:
            center_x, center_y = self.player_pos
        else:
            center_x, center_y = self.floor.width // 2, self.floor.height // 2

        # Calculate viewport bounds
        min_x = max(0, center_x - tiles_x // 2)
        max_x = min(self.floor.width - 1, min_x + tiles_x - 1)

        # Adjust min_x if we hit the right edge
        if max_x == self.floor.width - 1:
            min_x = max(0, max_x - tiles_x + 1)

        min_y = max(0, center_y - tiles_y // 2)
        max_y = min(self.floor.height - 1, min_y + tiles_y - 1)

        # Adjust min_y if we hit the bottom edge
        if max_y == self.floor.height - 1:
            min_y = max(0, max_y - tiles_y + 1)

        return (min_x, max_x, min_y, max_y)

    def _tile_to_screen(self, tile_x: int, tile_y: int) -> Tuple[int, int]:
        """Convert tile coordinates to screen coordinates.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            Tuple of (screen_x, screen_y)
        """
        min_x, _, min_y, _ = self._calculate_viewport()
        screen_x = (tile_x - min_x) * self.tile_size
        screen_y = (tile_y - min_y) * self.tile_size
        return (screen_x, screen_y)

    def _get_tile_at_position(self, x: int, y: int) -> Tuple[int, int]:
        """Get tile coordinates at screen position.

        Args:
            x: Screen X coordinate
            y: Screen Y coordinate

        Returns:
            Tuple of (tile_x, tile_y)
        """
        if not self.floor or self.tile_size == 0:
            return (0, 0)

        min_x, _, min_y, _ = self._calculate_viewport()
        tile_x = x // self.tile_size + min_x
        tile_y = y // self.tile_size + min_y

        # Clamp to valid range
        tile_x = max(0, min(self.floor.width - 1, tile_x))
        tile_y = max(0, min(self.floor.height - 1, tile_y))

        return (tile_x, tile_y)

    def _recalculate_tile_size(self) -> None:
        """Recalculate tile size based on widget and floor dimensions."""
        if not self.floor:
            return

        # Calculate tile size to fit the floor in the widget
        tile_size_x = self.width() // self.floor.width
        tile_size_y = self.height() // self.floor.height

        # Use the smaller size to ensure everything fits
        self.tile_size = max(1, min(tile_size_x, tile_size_y))

    def resizeEvent(self, event) -> None:
        """Handle resize event.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        self._recalculate_tile_size()

    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse move event for hover effects.

        Args:
            event: Mouse event
        """
        if self.floor and event:
            # Get position - event.position() returns QPointF
            pos_f = event.position()
            # Convert to QPoint
            pos_x = int(pos_f.x())
            pos_y = int(pos_f.y())
            
            new_hover = self._get_tile_at_position(pos_x, pos_y)

            if new_hover != self.hover_tile:
                self.hover_tile = new_hover
                self.update()
