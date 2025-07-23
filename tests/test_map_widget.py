"""Tests for the map widget - UTF Contract GAME-UI-002."""

import sys
from unittest.mock import MagicMock, patch

import pytest

try:
    from PyQt6.QtCore import QPoint, QRect, Qt
    from PyQt6.QtGui import QColor, QMouseEvent, QPainter
    from PyQt6.QtWidgets import QApplication, QWidget

    from client.widgets.map_widget import MapWidget
    from src.enums import TileType
    from src.models.floor import Floor

    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # Create dummy classes to prevent import errors
    QPoint = None
    QRect = None
    Qt = None
    QColor = None
    QPainter = None
    QMouseEvent = None
    QApplication = None
    QWidget = None
    MapWidget = None
    Floor = None
    TileType = None

# Skip all tests if PyQt6 is not available
pytestmark = pytest.mark.skipif(
    not PYQT6_AVAILABLE,
    reason="PyQt6 not installed - install with: pip install PyQt6",  # noqa: E501
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def map_widget(qapp):
    """Create a MapWidget instance for testing."""
    widget = MapWidget()
    widget.resize(600, 400)  # Set a reasonable size for testing
    yield widget
    widget.close()


@pytest.fixture
def sample_floor():
    """Create a sample floor for testing."""
    floor = Floor(seed=42)
    floor.generate()
    return floor


class TestMapWidgetInitialization:
    """Test map widget initialization."""

    def test_widget_creation(self, map_widget):
        """Test widget is created with correct defaults."""
        assert isinstance(map_widget, QWidget)
        assert map_widget.floor is None
        assert map_widget.player_pos is None
        assert map_widget.tile_size > 0

    def test_color_definitions(self, map_widget):
        """Test color definitions match specification."""
        assert map_widget.colors["background"] == QColor("#1a1a1a")
        assert map_widget.colors["wall"] == QColor("#666666")
        assert map_widget.colors["floor"] == QColor("#333333")
        assert map_widget.colors["player"] == QColor("#00ff00")
        assert map_widget.colors["monster"] == QColor("#ff0000")

    def test_widget_size_handling(self, map_widget):
        """Test widget handles size correctly."""
        map_widget.resize(800, 600)
        assert map_widget.width() == 800
        assert map_widget.height() == 600


class TestMapRendering:
    """Test map rendering functionality."""

    def test_paint_event_without_floor(self, map_widget):
        """Test paint event handles null floor gracefully."""
        # Create a mock painter
        with patch("client.widgets.map_widget.QPainter") as mock_painter_class:
            mock_painter = MagicMock()
            mock_painter_class.return_value = mock_painter

            # Trigger paint event
            map_widget.paintEvent(None)

            # Should fill background but not draw tiles
            mock_painter.fillRect.assert_called()

    def test_paint_event_with_floor(self, map_widget, sample_floor):
        """Test paint event renders floor correctly."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)

        with patch("client.widgets.map_widget.QPainter") as mock_painter_class:
            mock_painter = MagicMock()
            mock_painter_class.return_value = mock_painter

            # Trigger paint event
            map_widget.paintEvent(None)

            # Should draw background and tiles
            assert mock_painter.fillRect.call_count >= 1
            assert mock_painter.setBrush.call_count > 0

    def test_tile_size_calculation(self, map_widget, sample_floor):
        """Test tile size is calculated correctly."""
        map_widget.set_floor(sample_floor)

        # Widget is 600x400, floor is 20x20
        # Tile size should fit the smaller dimension
        expected_tile_size = min(600 // 20, 400 // 20)
        assert map_widget.tile_size == expected_tile_size

    def test_view_centering_on_player(self, map_widget, sample_floor):
        """Test view centers on player position."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(5, 5)

        # Calculate expected viewport
        viewport = map_widget._calculate_viewport()

        # Player should be in center of viewport when possible
        viewport_center_x = (viewport[0] + viewport[1]) // 2
        viewport_center_y = (viewport[2] + viewport[3]) // 2

        # Allow for edge cases where player is near map edge
        assert abs(viewport_center_x - 5) <= map_widget.width() // (
            2 * map_widget.tile_size
        )  # noqa: E501
        assert abs(viewport_center_y - 5) <= map_widget.height() // (
            2 * map_widget.tile_size
        )  # noqa: E501


class TestGameStateConnection:
    """Test connection to game state."""

    def test_set_floor(self, map_widget, sample_floor):
        """Test setting floor object."""
        map_widget.set_floor(sample_floor)
        assert map_widget.floor == sample_floor

    def test_set_player_position(self, map_widget):
        """Test setting player position."""
        map_widget.set_player_position(3, 4)
        assert map_widget.player_pos == (3, 4)

    def test_update_triggers_repaint(self, map_widget, sample_floor):
        """Test state changes trigger repaint."""
        with patch.object(map_widget, "update") as mock_update:
            map_widget.set_floor(sample_floor)
            mock_update.assert_called_once()

            map_widget.set_player_position(5, 5)
            assert mock_update.call_count == 2


class TestVisualFeedback:
    """Test visual feedback features."""

    def test_hover_highlight_calculation(self, map_widget, sample_floor):
        """Test hover tile calculation from mouse position."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)

        # Simulate mouse at specific position
        tile_x, tile_y = map_widget._get_tile_at_position(100, 100)

        # Should return valid tile coordinates
        assert 0 <= tile_x < sample_floor.width
        assert 0 <= tile_y < sample_floor.height

    def test_hover_highlight_updates(self, map_widget, sample_floor):
        """Test hover highlight triggers update."""
        map_widget.set_floor(sample_floor)

        with patch.object(map_widget, "update") as mock_update:
            # Create mouse move event
            event = MagicMock()
            event.position.return_value = QPoint(100, 100)

            map_widget.mouseMoveEvent(event)
            mock_update.assert_called()

    def test_combat_flash_state(self, map_widget):
        """Test combat flash state management."""
        # Flash a tile
        map_widget.flash_tile(5, 5, "combat")
        assert (5, 5) in map_widget.flashing_tiles

        # Clear flash
        map_widget.clear_flash(5, 5)
        assert (5, 5) not in map_widget.flashing_tiles

    def test_valid_move_highlighting(self, map_widget, sample_floor):
        """Test valid move tiles are tracked."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)

        # Set valid moves
        valid_moves = [(9, 10), (11, 10), (10, 9), (10, 11)]
        map_widget.set_valid_moves(valid_moves)

        assert map_widget.valid_moves == valid_moves


class TestResizeHandling:
    """Test widget resize handling."""

    def test_resize_event_updates_tile_size(self, map_widget, sample_floor, qapp):  # noqa: E501
        """Test resize recalculates tile size."""
        map_widget.set_floor(sample_floor)

        # Start with a size that gives tile_size = 30
        # 600/20 = 30, 600/20 = 30, so tile_size = 30
        map_widget.resize(600, 600)
        # Process events to ensure resize happens
        qapp.processEvents()
        map_widget._recalculate_tile_size()  # Force recalculation
        initial_tile_size = map_widget.tile_size
        assert initial_tile_size == 30

        # Resize widget to smaller size
        # 200/20 = 10, so tile_size should be 10
        map_widget.resize(200, 200)
        qapp.processEvents()
        map_widget._recalculate_tile_size()  # Force recalculation

        # Tile size should be recalculated
        assert map_widget.tile_size == 10
        assert map_widget.tile_size != initial_tile_size

    def test_resize_maintains_center(self, map_widget, sample_floor):
        """Test resize maintains player centering."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)

        # Resize widget
        map_widget.resize(800, 600)

        # View should still be centered on player
        viewport = map_widget._calculate_viewport()
        viewport_center_x = (viewport[0] + viewport[1]) // 2
        viewport_center_y = (viewport[2] + viewport[3]) // 2

        assert abs(viewport_center_x - 10) <= map_widget.width() // (
            2 * map_widget.tile_size
        )  # noqa: E501
        assert abs(viewport_center_y - 10) <= map_widget.height() // (
            2 * map_widget.tile_size
        )  # noqa: E501


class TestZoomFunctionality:
    """Test zoom functionality for map exploration."""

    def test_zoom_levels(self, map_widget):
        """Test zoom level constraints."""
        # Default zoom should be 1.0
        assert map_widget.zoom_level == 1.0

        # Test zoom in
        map_widget.zoom_in()
        assert map_widget.zoom_level == 1.25

        # Test zoom out
        map_widget.zoom_out()
        map_widget.zoom_out()
        assert map_widget.zoom_level == 0.75

    def test_zoom_limits(self, map_widget):
        """Test zoom min/max limits."""
        # Zoom out to minimum
        for _ in range(10):
            map_widget.zoom_out()
        assert map_widget.zoom_level >= 0.5  # Min zoom

        # Zoom in to maximum
        for _ in range(20):
            map_widget.zoom_in()
        assert map_widget.zoom_level <= 3.0  # Max zoom

    def test_zoom_tile_size_update(self, map_widget, sample_floor):
        """Test that zoom affects tile size."""
        map_widget.set_floor(sample_floor)
        base_tile_size = map_widget.tile_size

        # Zoom in should increase tile size
        map_widget.zoom_in()
        assert map_widget.tile_size > base_tile_size

        # Zoom out should decrease tile size
        map_widget.zoom_out()
        map_widget.zoom_out()
        assert map_widget.tile_size < base_tile_size

    def test_zoom_with_mouse_wheel(self, map_widget, sample_floor):
        """Test zoom with mouse wheel events."""
        map_widget.set_floor(sample_floor)
        initial_zoom = map_widget.zoom_level

        # Create wheel event for zoom in
        wheel_event = MagicMock()
        wheel_event.angleDelta.return_value.y.return_value = 120
        wheel_event.position.return_value = QPoint(100, 100)

        map_widget.wheelEvent(wheel_event)
        assert map_widget.zoom_level > initial_zoom

    def test_zoom_reset(self, map_widget):
        """Test zoom reset functionality."""
        # Change zoom
        map_widget.zoom_in()
        map_widget.zoom_in()
        assert map_widget.zoom_level != 1.0

        # Reset zoom
        map_widget.reset_zoom()
        assert map_widget.zoom_level == 1.0


class TestPerformance:
    """Test performance requirements."""

    def test_paint_performance(self, map_widget, sample_floor):
        """Test paint completes within frame time."""
        import time

        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)

        # Mock painter to avoid actual rendering
        with patch("client.widgets.map_widget.QPainter"):
            start = time.perf_counter()
            map_widget.paintEvent(None)
            elapsed = time.perf_counter() - start

            # Should complete in less than 16ms (60 FPS)
            assert elapsed < 0.016

    def test_memory_stability(self, map_widget, sample_floor):
        """Test memory usage remains stable."""
        import gc

        map_widget.set_floor(sample_floor)

        # Get initial memory state
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform multiple updates
        for i in range(100):
            map_widget.set_player_position(i % 20, i % 20)
            map_widget.update()

        # Check memory hasn't grown significantly
        gc.collect()
        final_objects = len(gc.get_objects())

        # Allow for some growth but not linear with updates
        assert final_objects - initial_objects < 50


class TestMiniMapOverlay:
    """Test mini-map overlay functionality."""

    def test_minimap_visibility_toggle(self, map_widget):
        """Test mini-map can be toggled on/off."""
        # Should be hidden by default
        assert not map_widget.show_minimap

        # Toggle on
        map_widget.toggle_minimap()
        assert map_widget.show_minimap

        # Toggle off
        map_widget.toggle_minimap()
        assert not map_widget.show_minimap

    def test_minimap_position(self, map_widget):
        """Test mini-map position in corner."""
        map_widget.show_minimap = True

        # Get minimap rect
        rect = map_widget._get_minimap_rect()

        # Should be in top-right corner with margin
        assert rect.x() > map_widget.width() - 200
        assert rect.y() < 50
        assert rect.width() == 150
        assert rect.height() == 150

    def test_minimap_scale_calculation(self, map_widget, sample_floor):
        """Test mini-map scale calculation."""
        map_widget.set_floor(sample_floor)
        map_widget.show_minimap = True

        scale = map_widget._calculate_minimap_scale()

        # Scale should fit entire floor in minimap
        assert scale > 0
        assert scale * sample_floor.width <= 150
        assert scale * sample_floor.height <= 150

    def test_minimap_player_indicator(self, map_widget, sample_floor):
        """Test player position shown on minimap."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)
        map_widget.show_minimap = True

        # Calculate player position on minimap
        minimap_pos = map_widget._player_pos_on_minimap()

        # Should be within minimap bounds
        minimap_rect = map_widget._get_minimap_rect()
        assert minimap_rect.contains(minimap_pos)

    def test_minimap_viewport_indicator(self, map_widget, sample_floor):
        """Test viewport rectangle shown on minimap."""
        map_widget.set_floor(sample_floor)
        map_widget.set_player_position(10, 10)
        map_widget.show_minimap = True

        # Get viewport rect on minimap
        viewport_rect = map_widget._viewport_rect_on_minimap()

        # Should be within minimap bounds
        minimap_rect = map_widget._get_minimap_rect()
        assert minimap_rect.contains(viewport_rect)
