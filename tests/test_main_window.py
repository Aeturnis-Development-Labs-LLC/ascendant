"""Tests for the main window - UTF Contracts GAME-UI-001, GAME-UI-004."""

import sys
from unittest.mock import Mock, patch

import pytest

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeyEvent
    from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget

    from client.main_window import MainWindow

    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # Create dummy classes to prevent import errors
    Qt = None
    QKeyEvent = None
    QApplication = None
    QHBoxLayout = None
    QWidget = None
    MainWindow = None

# Skip all tests if PyQt6 is not available
pytestmark = pytest.mark.skipif(
    not PYQT6_AVAILABLE, reason="PyQt6 not installed - install with: pip install PyQt6"
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't quit the app as it might be reused


@pytest.fixture
def main_window(qapp):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    yield window
    window.close()


class TestMainWindowLayout:
    """Test main window layout meets GAME-UI-001 requirements."""

    def test_window_default_size(self, main_window):
        """Test window starts with correct default size."""
        assert main_window.width() == 1280
        assert main_window.height() == 720

    def test_window_minimum_size(self, main_window):
        """Test window has correct minimum size."""
        assert main_window.minimumWidth() == 1024
        assert main_window.minimumHeight() == 600

    def test_window_title(self, main_window):
        """Test window has correct title with version."""
        assert "Ascendant: The Eternal Spire" in main_window.windowTitle()
        assert "v" in main_window.windowTitle()  # Should include version

    def test_three_panel_layout(self, main_window):
        """Test window has three panels with correct layout."""
        central_widget = main_window.centralWidget()
        assert central_widget is not None

        layout = central_widget.layout()
        assert isinstance(layout, QHBoxLayout)
        assert layout.count() == 3

    def test_panel_stretch_ratios(self, main_window):
        """Test panels have correct 20-60-20 stretch ratios."""
        layout = main_window.centralWidget().layout()

        # Check stretch factors
        assert layout.stretch(0) == 20  # Left panel
        assert layout.stretch(1) == 60  # Center panel
        assert layout.stretch(2) == 20  # Right panel

    def test_panels_exist(self, main_window):
        """Test all three panels exist."""
        assert hasattr(main_window, "left_panel")
        assert hasattr(main_window, "center_panel")
        assert hasattr(main_window, "right_panel")

        assert isinstance(main_window.left_panel, QWidget)
        assert isinstance(main_window.center_panel, QWidget)
        assert isinstance(main_window.right_panel, QWidget)

    def test_status_bar_exists(self, main_window):
        """Test status bar exists with version."""
        status_bar = main_window.statusBar()
        assert status_bar is not None
        assert status_bar.isVisible()

        # Check for version widget
        # Status bar should have at least one permanent widget (version label)
        assert len(status_bar.children()) > 1  # Has widgets


class TestMenuSystem:
    """Test menu system meets GAME-UI-004 requirements."""

    def test_menu_bar_exists(self, main_window):
        """Test menu bar exists."""
        menubar = main_window.menuBar()
        assert menubar is not None
        assert menubar.isVisible()

    def test_file_menu_structure(self, main_window):
        """Test File menu has correct items."""
        menubar = main_window.menuBar()
        file_menu = None

        # Find File menu
        for action in menubar.actions():
            if action.text() == "&File":
                file_menu = action.menu()
                break

        assert file_menu is not None

        # Check menu items
        actions = [a.text() for a in file_menu.actions() if not a.isSeparator()]
        assert "&New Game" in actions
        assert "&Save" in actions
        assert "&Load" in actions
        assert "&Quit" in actions

    def test_options_menu_structure(self, main_window):
        """Test Options menu has correct items."""
        menubar = main_window.menuBar()
        options_menu = None

        # Find Options menu
        for action in menubar.actions():
            if action.text() == "&Options":
                options_menu = action.menu()
                break

        assert options_menu is not None

        # Check menu items
        actions = [a.text() for a in options_menu.actions()]
        assert "&Settings" in actions
        assert "&Controls" in actions

    def test_help_menu_structure(self, main_window):
        """Test Help menu has correct items."""
        menubar = main_window.menuBar()
        help_menu = None

        # Find Help menu
        for action in menubar.actions():
            if action.text() == "&Help":
                help_menu = action.menu()
                break

        assert help_menu is not None

        # Check menu items
        actions = [a.text() for a in help_menu.actions()]
        assert "&About" in actions
        assert "&How to Play" in actions

    def test_keyboard_shortcuts(self, main_window):
        """Test menu items have appropriate keyboard shortcuts."""
        menubar = main_window.menuBar()

        # Check File menu shortcuts
        for action in menubar.actions():
            if action.text() == "&File":
                file_menu = action.menu()
                for menu_action in file_menu.actions():
                    if menu_action.text() == "&New Game":
                        assert menu_action.shortcut().toString() == "Ctrl+N"
                    elif menu_action.text() == "&Save":
                        assert menu_action.shortcut().toString() == "Ctrl+S"
                    elif menu_action.text() == "&Load":
                        assert menu_action.shortcut().toString() == "Ctrl+L"
                    elif menu_action.text() == "&Quit":
                        assert menu_action.shortcut().toString() == "Ctrl+Q"

    @patch("builtins.print")
    def test_menu_actions_connected(self, mock_print, main_window):
        """Test menu actions are connected to handlers."""
        menubar = main_window.menuBar()

        # Test New Game action
        for action in menubar.actions():
            if action.text() == "&File":
                file_menu = action.menu()
                for menu_action in file_menu.actions():
                    if menu_action.text() == "&New Game":
                        menu_action.trigger()
                        mock_print.assert_called_with("New Game clicked")
                        break


class TestKeyboardHandling:
    """Test keyboard event handling."""

    def test_keyboard_handler_not_set(self, main_window, qapp):
        """Test keyboard events are handled when no handler is set."""
        # Test game key (WASD)
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_W, Qt.KeyboardModifier.NoModifier)
        main_window.keyPressEvent(event)
        assert event.isAccepted()

    def test_keyboard_handler_forwarding(self, main_window, qapp):
        """Test keyboard events are forwarded to handler when set."""
        mock_handler = Mock()
        main_window.set_keyboard_handler(mock_handler)

        # Send key event
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_W, Qt.KeyboardModifier.NoModifier)
        main_window.keyPressEvent(event)

        # Check handler was called
        mock_handler.assert_called_once_with(event)

    def test_game_keys_prevented(self, main_window, qapp):
        """Test game keys are prevented from default behavior."""
        # Test all game keys
        game_keys = [
            Qt.Key.Key_W,
            Qt.Key.Key_A,
            Qt.Key.Key_S,
            Qt.Key.Key_D,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
        ]

        for key in game_keys:
            event = QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier)
            main_window.keyPressEvent(event)
            assert event.isAccepted()


class TestWindowResize:
    """Test window resizing behavior."""

    def test_window_is_resizable(self, main_window):
        """Test window can be resized."""
        # Resize window
        main_window.resize(1400, 800)
        assert main_window.width() == 1400
        assert main_window.height() == 800

    def test_minimum_size_enforced(self, main_window):
        """Test window cannot be resized below minimum."""
        # Try to resize below minimum
        main_window.resize(800, 400)

        # Size should be clamped to minimum
        assert main_window.width() >= 1024
        assert main_window.height() >= 600

    def test_panel_ratios_maintained_on_resize(self, main_window, qapp):
        """Test panel ratios are maintained when window is resized."""
        # Get initial layout
        layout = main_window.centralWidget().layout()

        # Resize window
        main_window.resize(1600, 900)
        qapp.processEvents()

        # Check stretch factors are still correct
        assert layout.stretch(0) == 20  # Left panel
        assert layout.stretch(1) == 60  # Center panel
        assert layout.stretch(2) == 20  # Right panel
