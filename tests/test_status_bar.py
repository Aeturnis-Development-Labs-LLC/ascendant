"""Tests for status bar widget - UTF Contract GAME-UI-005."""

import sys
from unittest.mock import patch

import pytest

try:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication, QLabel

    from client.widgets.status_bar import MessagePriority, StatusBar

    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QApplication = None
    QTimer = None
    StatusBar = None
    MessagePriority = None

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


@pytest.fixture
def status_bar(qapp):
    """Create a StatusBar instance for testing."""
    bar = StatusBar()
    yield bar
    bar.close()


class TestStatusBarInitialization:
    """Test status bar initialization."""

    def test_status_bar_creation(self, status_bar):
        """Test status bar is created correctly."""
        assert isinstance(status_bar, QLabel)
        assert status_bar.text() == ""
        assert hasattr(status_bar, "show_message")
        assert hasattr(status_bar, "clear_message")

    def test_message_priority_enum(self):
        """Test message priority enum exists."""
        assert MessagePriority.FLAVOR < MessagePriority.INFO
        assert MessagePriority.INFO < MessagePriority.COMBAT
        assert MessagePriority.COMBAT.value == 3  # Highest priority


class TestMessageDisplay:
    """Test message display functionality."""

    def test_show_basic_message(self, status_bar):
        """Test showing a basic message."""
        status_bar.show_message("Hello, player!", MessagePriority.INFO)
        assert status_bar.text() == "Hello, player!"

    def test_message_colors_by_priority(self, status_bar):
        """Test messages have different colors based on priority."""
        # Flavor text - gray
        status_bar.show_message("The wind blows...", MessagePriority.FLAVOR)
        style = status_bar.styleSheet()
        assert "gray" in style or "#808080" in style

        # Info text - white
        status_bar.show_message("You found a key!", MessagePriority.INFO)
        style = status_bar.styleSheet()
        assert "white" in style or "#ffffff" in style

        # Combat text - red
        status_bar.show_message("You take 10 damage!", MessagePriority.COMBAT)
        style = status_bar.styleSheet()
        assert "red" in style or "#ff0000" in style

    def test_custom_message_colors(self, status_bar):
        """Test custom colors can be specified."""
        status_bar.show_message(
            "Poisoned!", MessagePriority.COMBAT, color="#00ff00"  # Green for poison
        )
        style = status_bar.styleSheet()
        assert "#00ff00" in style


class TestMessagePriority:
    """Test message priority system."""

    def test_higher_priority_overwrites(self, status_bar):
        """Test higher priority messages overwrite lower ones."""
        status_bar.show_message("Low priority", MessagePriority.FLAVOR)
        assert status_bar.text() == "Low priority"

        status_bar.show_message("High priority", MessagePriority.COMBAT)
        assert status_bar.text() == "High priority"

    def test_lower_priority_ignored(self, status_bar):
        """Test lower priority messages don't overwrite higher ones."""
        status_bar.show_message("High priority", MessagePriority.COMBAT)
        status_bar.show_message("Low priority", MessagePriority.FLAVOR)

        # Should still show high priority message
        assert status_bar.text() == "High priority"

    def test_same_priority_overwrites(self, status_bar):
        """Test same priority messages overwrite each other."""
        status_bar.show_message("First info", MessagePriority.INFO)
        status_bar.show_message("Second info", MessagePriority.INFO)

        assert status_bar.text() == "Second info"


class TestAutoClear:
    """Test auto-clear functionality."""

    def test_auto_clear_timer(self, status_bar, qapp):
        """Test messages auto-clear after timeout."""
        with patch.object(QTimer, "singleShot") as mock_timer:
            status_bar.show_message("Temporary message", MessagePriority.INFO)

            # Check timer was set for 5 seconds
            mock_timer.assert_called_once()
            args = mock_timer.call_args[0]
            assert args[0] == 5000  # 5 seconds in milliseconds

    def test_custom_timeout(self, status_bar):
        """Test custom timeout can be specified."""
        with patch.object(QTimer, "singleShot") as mock_timer:
            status_bar.show_message(
                "Quick message", MessagePriority.INFO, timeout=2000  # 2 seconds
            )

            args = mock_timer.call_args[0]
            assert args[0] == 2000

    def test_no_auto_clear_option(self, status_bar):
        """Test messages can be set to not auto-clear."""
        with patch.object(QTimer, "singleShot") as mock_timer:
            status_bar.show_message("Permanent message", MessagePriority.INFO, auto_clear=False)

            # Timer should not be called
            mock_timer.assert_not_called()

    def test_clear_resets_priority(self, status_bar):
        """Test clearing message resets priority."""
        status_bar.show_message("High priority", MessagePriority.COMBAT)
        status_bar.clear_message()

        # Now low priority should work
        status_bar.show_message("Low priority", MessagePriority.FLAVOR)
        assert status_bar.text() == "Low priority"


class TestMessageQueue:
    """Test message queuing functionality."""

    def test_message_history(self, status_bar):
        """Test status bar maintains message history."""
        messages = [
            ("First message", MessagePriority.INFO),
            ("Second message", MessagePriority.COMBAT),
            ("Third message", MessagePriority.FLAVOR),
        ]

        for text, priority in messages:
            status_bar.show_message(text, priority)

        history = status_bar.get_message_history()
        assert len(history) >= 3
        assert history[-1][0] == "Third message"

    def test_history_limit(self, status_bar):
        """Test message history has a limit."""
        # Add many messages
        for i in range(100):
            status_bar.show_message(f"Message {i}", MessagePriority.INFO)

        history = status_bar.get_message_history()
        assert len(history) <= 50  # Reasonable history limit


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_message_handling(self, status_bar):
        """Test handling of empty messages."""
        status_bar.show_message("", MessagePriority.INFO)
        assert status_bar.text() == ""

    def test_very_long_messages(self, status_bar):
        """Test handling of very long messages."""
        long_message = "A" * 500
        status_bar.show_message(long_message, MessagePriority.INFO)

        # Should truncate or handle gracefully
        displayed_text = status_bar.text()
        assert len(displayed_text) <= 200  # Reasonable limit

    def test_special_characters(self, status_bar):
        """Test handling of special characters in messages."""
        special_message = "You found <gold>! & gained 100% more XP"
        status_bar.show_message(special_message, MessagePriority.INFO)

        # Should handle HTML entities properly
        assert status_bar.text() == special_message
