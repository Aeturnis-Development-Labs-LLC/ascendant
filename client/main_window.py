"""Main window for Ascendant PyQt6 client."""

from typing import TYPE_CHECKING, Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

# Import version from main package
try:
    from src import __version__
except ImportError:
    __version__ = "Unknown"

# Import our custom widgets
if TYPE_CHECKING:
    from client.widgets.map_widget import MapWidget

try:
    from client.widgets.map_widget import MapWidget  # noqa: F811

    HAS_MAP_WIDGET = True
except ImportError:
    HAS_MAP_WIDGET = False


class MainWindow(QMainWindow):
    """Main game window with three-panel layout."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle(f"Ascendant: The Eternal Spire v{__version__}")
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(1024, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create three panels with fixed ratios
        self.left_panel = self._create_panel("Left Panel", "20%")
        self.center_panel = self._create_center_panel()
        self.right_panel = self._create_panel("Right Panel", "20%")

        # Add panels to layout with stretch factors (20-60-20 ratio)
        layout.addWidget(self.left_panel, 20)
        layout.addWidget(self.center_panel, 60)
        layout.addWidget(self.right_panel, 20)

        # Create menu bar
        self._create_menu_bar()

        # Create status bar with version
        self._create_status_bar()

        # Initialize keyboard handler (will be connected later)
        self.keyboard_handler: Optional[Callable[[QKeyEvent], None]] = None

        # Initialize map widget reference
        self.map_widget: Optional["MapWidget"] = None

    def _create_panel(self, text: str, size: str) -> QWidget:
        """Create a panel widget with placeholder content.

        Args:
            text: Panel label text
            size: Panel size description

        Returns:
            Panel widget
        """
        panel = QWidget()
        panel.setStyleSheet(
            "QWidget { background-color: #2b2b2b; border: 1px solid #555; }"
        )  # noqa: E501

        # Add placeholder label
        label = QLabel(f"{text}\n({size})")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("QLabel { color: #ffffff; font-size: 14px; }")

        # Simple layout for the panel
        layout = QHBoxLayout(panel)
        layout.addWidget(label)

        return panel

    def _create_center_panel(self) -> QWidget:
        """Create the center panel with map widget.

        Returns:
            Center panel widget
        """
        panel = QWidget()
        panel.setStyleSheet(
            "QWidget { background-color: #2b2b2b; border: 1px solid #555; }"
        )  # noqa: E501

        # Create layout for center panel
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create map widget if available
        if HAS_MAP_WIDGET:
            self.map_widget = MapWidget()
            layout.addWidget(self.map_widget)
        else:
            # Fallback to label if MapWidget not available
            label = QLabel("Map Display\n(60%)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("QLabel { color: #ffffff; font-size: 14px; }")
            layout.addWidget(label)

        return panel

    def _create_menu_bar(self) -> None:
        """Create the menu bar with File, Options, and Help menus."""
        menubar = self.menuBar()
        if not menubar:
            return

        # File menu
        file_menu = menubar.addMenu("&File")
        if not file_menu:
            return

        new_game_action = QAction("&New Game", self)
        new_game_action.setShortcut("Ctrl+N")
        new_game_action.triggered.connect(self._on_new_game)
        file_menu.addAction(new_game_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        load_action = QAction("&Load", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self._on_load)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Options menu
        options_menu = menubar.addMenu("&Options")
        if not options_menu:
            return

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._on_settings)
        options_menu.addAction(settings_action)

        controls_action = QAction("&Controls", self)
        controls_action.triggered.connect(self._on_controls)
        options_menu.addAction(controls_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        if not help_menu:
            return

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        how_to_play_action = QAction("&How to Play", self)
        how_to_play_action.setShortcut("F1")
        how_to_play_action.triggered.connect(self._on_how_to_play)
        help_menu.addAction(how_to_play_action)

        # Add view menu for zoom and minimap
        view_menu = menubar.addMenu("&View")
        if view_menu:
            zoom_in_action = QAction("Zoom &In", self)
            zoom_in_action.setShortcut("Ctrl++")
            zoom_in_action.triggered.connect(self._on_zoom_in)
            view_menu.addAction(zoom_in_action)

            zoom_out_action = QAction("Zoom &Out", self)
            zoom_out_action.setShortcut("Ctrl+-")
            zoom_out_action.triggered.connect(self._on_zoom_out)
            view_menu.addAction(zoom_out_action)

            reset_zoom_action = QAction("&Reset Zoom", self)
            reset_zoom_action.setShortcut("Ctrl+0")
            reset_zoom_action.triggered.connect(self._on_reset_zoom)
            view_menu.addAction(reset_zoom_action)

            view_menu.addSeparator()

            minimap_action = QAction("Toggle &Minimap", self)
            minimap_action.setShortcut("M")
            minimap_action.triggered.connect(self._on_toggle_minimap)
            view_menu.addAction(minimap_action)

    def _create_status_bar(self) -> None:
        """Create the status bar with version information."""
        status_bar = self.statusBar()
        if not status_bar:
            return
        status_bar.setStyleSheet(
            "QStatusBar { background-color: #1e1e1e; color: #ffffff; }"
        )  # noqa: E501

        # Add version label on the right
        version_label = QLabel(f"v{__version__}")
        version_label.setStyleSheet("QLabel { color: #888888; padding: 0 10px; }")  # noqa: E501
        status_bar.addPermanentWidget(version_label)

        # Set initial message
        status_bar.showMessage("Ready", 5000)

    def keyPressEvent(self, event: Optional[QKeyEvent]) -> None:
        """Handle keyboard events.

        Args:
            event: The key press event
        """
        if not event:
            return
        # Forward to keyboard handler if set
        if self.keyboard_handler:
            self.keyboard_handler(event)
        else:
            # Default behavior - prevent propagation of game keys
            key = event.key()
            if key in (
                Qt.Key.Key_W,
                Qt.Key.Key_A,
                Qt.Key.Key_S,
                Qt.Key.Key_D,
                Qt.Key.Key_Up,
                Qt.Key.Key_Down,
                Qt.Key.Key_Left,
                Qt.Key.Key_Right,
            ):
                event.accept()
            else:
                super().keyPressEvent(event)

    def set_keyboard_handler(self, handler: Callable[[QKeyEvent], None]) -> None:  # noqa: E501
        """Set the keyboard event handler.

        Args:
            handler: Callable that takes a QKeyEvent
        """
        self.keyboard_handler = handler

    # Menu action handlers (placeholders for now)
    def _on_new_game(self) -> None:
        """Handle new game action."""
        print("New Game clicked")

    def _on_save(self) -> None:
        """Handle save action."""
        print("Save clicked")

    def _on_load(self) -> None:
        """Handle load action."""
        print("Load clicked")

    def _on_settings(self) -> None:
        """Handle settings action."""
        print("Settings clicked")

    def _on_controls(self) -> None:
        """Handle controls action."""
        print("Controls clicked")

    def _on_about(self) -> None:
        """Handle about action."""
        print("About clicked")

    def _on_how_to_play(self) -> None:
        """Handle how to play action."""
        print("How to Play clicked")

    def _on_zoom_in(self) -> None:
        """Handle zoom in action."""
        if self.map_widget:
            self.map_widget.zoom_in()

    def _on_zoom_out(self) -> None:
        """Handle zoom out action."""
        if self.map_widget:
            self.map_widget.zoom_out()

    def _on_reset_zoom(self) -> None:
        """Handle reset zoom action."""
        if self.map_widget:
            self.map_widget.reset_zoom()

    def _on_toggle_minimap(self) -> None:
        """Handle toggle minimap action."""
        if self.map_widget:
            self.map_widget.toggle_minimap()

    # Game state methods
    def set_floor(self, floor) -> None:
        """Set the floor to display in the map widget.

        Args:
            floor: Floor object to display
        """
        if self.map_widget:
            self.map_widget.set_floor(floor)

    def set_player_position(self, x: int, y: int) -> None:
        """Set the player position on the map.

        Args:
            x: Player X coordinate
            y: Player Y coordinate
        """
        if self.map_widget:
            self.map_widget.set_player_position(x, y)
