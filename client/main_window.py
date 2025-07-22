"""Main window for Ascendant PyQt6 client."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main game window with three-panel layout."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Ascendant: The Eternal Spire")
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
        self.center_panel = self._create_panel("Center Panel", "60%")
        self.right_panel = self._create_panel("Right Panel", "20%")

        # Add panels to layout with stretch factors (20-60-20 ratio)
        layout.addWidget(self.left_panel, 20)
        layout.addWidget(self.center_panel, 60)
        layout.addWidget(self.right_panel, 20)

        # Create menu bar
        self._create_menu_bar()

        # Initialize keyboard handler (will be connected later)
        self.keyboard_handler = None

    def _create_panel(self, text: str, size: str) -> QWidget:
        """Create a panel widget with placeholder content.

        Args:
            text: Panel label text
            size: Panel size description

        Returns:
            Panel widget
        """
        panel = QWidget()
        panel.setStyleSheet("QWidget { background-color: #2b2b2b; border: 1px solid #555; }")

        # Add placeholder label
        label = QLabel(f"{text}\n({size})")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("QLabel { color: #ffffff; font-size: 14px; }")

        # Simple layout for the panel
        layout = QHBoxLayout(panel)
        layout.addWidget(label)

        return panel

    def _create_menu_bar(self):
        """Create the menu bar with File, Options, and Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

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

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._on_settings)
        options_menu.addAction(settings_action)

        controls_action = QAction("&Controls", self)
        controls_action.triggered.connect(self._on_controls)
        options_menu.addAction(controls_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        how_to_play_action = QAction("&How to Play", self)
        how_to_play_action.setShortcut("F1")
        how_to_play_action.triggered.connect(self._on_how_to_play)
        help_menu.addAction(how_to_play_action)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events.

        Args:
            event: The key press event
        """
        # Forward to keyboard handler if set
        if self.keyboard_handler:
            self.keyboard_handler(event)
        else:
            # Default behavior - prevent propagation of game keys
            key = event.key()
            if key in (Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D,
                      Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
                event.accept()
            else:
                super().keyPressEvent(event)

    def set_keyboard_handler(self, handler):
        """Set the keyboard event handler.

        Args:
            handler: Callable that takes a QKeyEvent
        """
        self.keyboard_handler = handler

    # Menu action handlers (placeholders for now)
    def _on_new_game(self):
        """Handle new game action."""
        print("New Game clicked")

    def _on_save(self):
        """Handle save action."""
        print("Save clicked")

    def _on_load(self):
        """Handle load action."""
        print("Load clicked")

    def _on_settings(self):
        """Handle settings action."""
        print("Settings clicked")

    def _on_controls(self):
        """Handle controls action."""
        print("Controls clicked")

    def _on_about(self):
        """Handle about action."""
        print("About clicked")

    def _on_how_to_play(self):
        """Handle how to play action."""
        print("How to Play clicked")