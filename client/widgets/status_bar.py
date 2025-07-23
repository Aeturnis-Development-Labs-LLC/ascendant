"""Status bar widget for displaying game messages with priority system."""

from enum import IntEnum
from typing import List, Optional, Tuple

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel


class MessagePriority(IntEnum):
    """Message priority levels for status bar."""

    FLAVOR = 1  # Atmospheric/flavor text
    INFO = 2  # General information
    COMBAT = 3  # Combat messages (highest priority)


class StatusBar(QLabel):
    """Status bar widget with message priority and auto-clear."""

    def __init__(self, parent=None):
        """Initialize the status bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current message state
        self._current_priority = 0
        self._clear_timer: Optional[QTimer] = None

        # Message history
        self._message_history: List[Tuple[str, MessagePriority, str]] = []
        self._history_limit = 50

        # Default styling
        self.setStyleSheet("QLabel { padding: 5px; }")

    def show_message(
        self,
        text: str,
        priority: MessagePriority,
        color: Optional[str] = None,
        timeout: int = 5000,
        auto_clear: bool = True,
    ) -> None:
        """Show a message in the status bar.

        Args:
            text: Message text to display
            priority: Message priority level
            color: Optional custom color (defaults based on priority)
            timeout: Auto-clear timeout in milliseconds (default 5000)
            auto_clear: Whether to auto-clear the message
        """
        # Truncate very long messages
        max_length = 200
        if len(text) > max_length:
            text = text[: max_length - 3] + "..."

        # Check priority - only skip if lower priority AND we have text
        if priority < self._current_priority and self.text():
            # Lower priority message, but still add to history
            if color is None:
                if priority == MessagePriority.FLAVOR:
                    color = "#808080"  # Gray
                elif priority == MessagePriority.INFO:
                    color = "#ffffff"  # White
                elif priority == MessagePriority.COMBAT:
                    color = "#ff0000"  # Red
            self._add_to_history(text, priority, color)
            return

        # Set the message
        self.setText(text)
        self._current_priority = priority

        # Determine color
        if color is None:
            if priority == MessagePriority.FLAVOR:
                color = "#808080"  # Gray
            elif priority == MessagePriority.INFO:
                color = "#ffffff"  # White
            elif priority == MessagePriority.COMBAT:
                color = "#ff0000"  # Red

        # Apply styling
        self.setStyleSheet(f"QLabel {{ padding: 5px; color: {color}; }}")

        # Add to history
        self._add_to_history(text, priority, color)

        # Handle auto-clear
        if auto_clear and text:  # Don't set timer for empty messages
            self._set_clear_timer(timeout)
        elif self._clear_timer:
            self._clear_timer.stop()
            self._clear_timer = None

    def clear_message(self) -> None:
        """Clear the current message and reset priority."""
        self.setText("")
        self._current_priority = 0

        if self._clear_timer:
            self._clear_timer.stop()
            self._clear_timer = None

    def get_message_history(self) -> List[Tuple[str, MessagePriority, str]]:
        """Get the message history.

        Returns:
            List of (text, priority, color) tuples
        """
        return self._message_history.copy()

    def _add_to_history(self, text: str, priority: MessagePriority, color: str) -> None:
        """Add a message to the history.

        Args:
            text: Message text
            priority: Message priority
            color: Message color
        """
        self._message_history.append((text, priority, color))

        # Trim history if needed
        if len(self._message_history) > self._history_limit:
            self._message_history = self._message_history[-self._history_limit:]

    def _set_clear_timer(self, timeout: int) -> None:
        """Set the auto-clear timer.

        Args:
            timeout: Timeout in milliseconds
        """
        # Stop existing timer
        if self._clear_timer:
            self._clear_timer.stop()

        # Create new timer
        QTimer.singleShot(timeout, self.clear_message)
