"""Info panel widget with tabs for inventory, combat log, and statistics."""

from typing import Any, Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class InventoryGrid(QWidget):
    """Grid-based inventory display."""

    # Signal emitted when slot is clicked
    slot_clicked = pyqtSignal(int)

    def __init__(self, rows=5, cols=8, parent=None):
        """Initialize the inventory grid.

        Args:
            rows: Number of rows
            cols: Number of columns
            parent: Parent widget
        """
        super().__init__(parent)

        self.rows = rows
        self.cols = cols
        self.total_slots = rows * cols

        # Storage for items
        self._items: Dict[int, Any] = {}

        # Create grid of buttons
        self._slots: Dict[int, QPushButton] = {}
        self._setup_grid()

    def _setup_grid(self):
        """Set up the inventory grid."""
        layout = QGridLayout(self)
        layout.setSpacing(2)

        for i in range(self.total_slots):
            row = i // self.cols
            col = i % self.cols

            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #333;
                    border: 1px solid #555;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """
            )

            # Connect click signal
            btn.clicked.connect(lambda checked, slot=i: self.slot_clicked.emit(slot))

            self._slots[i] = btn
            layout.addWidget(btn, row, col)

    def add_item(self, item: Any, slot: int) -> bool:
        """Add an item to a specific slot.

        Args:
            item: Item to add
            slot: Slot index

        Returns:
            True if item was added successfully
        """
        if slot < 0 or slot >= self.total_slots:
            return False

        self._items[slot] = item

        # Update button display
        btn = self._slots[slot]
        if hasattr(item, "name"):
            # Use first letter of item name
            btn.setText(item.name[0].upper())
        else:
            btn.setText("?")

        return True

    def remove_item(self, slot: int) -> Any:
        """Remove an item from a slot.

        Args:
            slot: Slot index

        Returns:
            The removed item, or None
        """
        if slot not in self._items:
            return None

        item = self._items.pop(slot)
        self._slots[slot].setText("")
        return item

    def get_item(self, slot: int) -> Any:
        """Get the item in a specific slot.

        Args:
            slot: Slot index

        Returns:
            The item, or None
        """
        return self._items.get(slot)

    def clear_items(self):
        """Clear all items from the inventory."""
        self._items.clear()
        for btn in self._slots.values():
            btn.setText("")

    def click_slot(self, slot: int):
        """Programmatically click a slot (for testing)."""
        if slot in self._slots:
            self._slots[slot].click()


class StatisticsDisplay(QTextEdit):
    """Display for game statistics."""

    def __init__(self, parent=None):
        """Initialize the statistics display."""
        super().__init__(parent)

        self.setReadOnly(True)
        self._stats: Dict[str, Any] = {}
        self._categories = ["Combat", "Exploration", "Items", "Deaths"]

        # Initialize display
        self._update_display()

    def get_categories(self) -> list:
        """Get the statistics categories."""
        return self._categories.copy()

    def update_stat(self, name: str, value: Any, is_percentage: bool = False):
        """Update a statistic value.

        Args:
            name: Statistic name
            value: Statistic value
            is_percentage: Whether to display as percentage
        """
        if is_percentage:
            self._stats[name] = (value, "%")
        else:
            self._stats[name] = (value, "")

        self._update_display()

    def _update_display(self):
        """Update the display text."""
        lines = []

        # Group stats by category (simple heuristic)
        combat_stats = []
        exploration_stats = []
        item_stats = []
        death_stats = []
        other_stats = []

        for name, (value, suffix) in self._stats.items():
            line = f"{name}: {value}{suffix}"

            # Simple categorization based on keywords
            name_lower = name.lower()
            if any(word in name_lower for word in ["kill", "damage", "hit", "critical"]):
                combat_stats.append(line)
            elif any(word in name_lower for word in ["floor", "room", "explore"]):
                exploration_stats.append(line)
            elif any(word in name_lower for word in ["item", "loot", "found"]):
                item_stats.append(line)
            elif "death" in name_lower:
                death_stats.append(line)
            else:
                other_stats.append(line)

        # Build display text
        if combat_stats:
            lines.append("=== Combat ===")
            lines.extend(combat_stats)
            lines.append("")

        if exploration_stats:
            lines.append("=== Exploration ===")
            lines.extend(exploration_stats)
            lines.append("")

        if item_stats:
            lines.append("=== Items ===")
            lines.extend(item_stats)
            lines.append("")

        if death_stats:
            lines.append("=== Deaths ===")
            lines.extend(death_stats)
            lines.append("")

        if other_stats:
            lines.append("=== Other ===")
            lines.extend(other_stats)

        self.setPlainText("\n".join(lines))


class InfoPanel(QWidget):
    """Information panel with tabs for inventory, combat log, and statistics."""

    # Signal emitted when inventory slot is clicked
    inventory_slot_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize the info panel."""
        super().__init__(parent)

        # Create widgets
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Create all the widgets."""
        # Tab widget
        self.tab_widget = QTabWidget()

        # Inventory tab
        self.inventory_grid = InventoryGrid()
        self.inventory_grid.slot_clicked.connect(self.inventory_slot_clicked.emit)

        # Combat log tab
        self.combat_log = QTextEdit()
        self.combat_log.setReadOnly(True)
        self._combat_log_lines = []
        self._max_combat_log_lines = 500

        # Statistics tab
        self.statistics_display = StatisticsDisplay()

        # Add tabs
        self.tab_widget.addTab(self.inventory_grid, "Inventory")
        self.tab_widget.addTab(self.combat_log, "Combat Log")
        self.tab_widget.addTab(self.statistics_display, "Statistics")

        # Floor info (always visible)
        self.floor_info_label = QLabel("Floor 1: Starting Area")
        self.floor_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.floor_info_label.setStyleSheet(
            """
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #555;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )

    def _setup_layout(self):
        """Set up the widget layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget takes most space
        layout.addWidget(self.tab_widget, 1)

        # Floor info at bottom
        layout.addWidget(self.floor_info_label)

    def add_inventory_item(self, item: Any, slot: int):
        """Add an item to the inventory.

        Args:
            item: Item to add
            slot: Slot index
        """
        self.inventory_grid.add_item(item, slot)

    def add_combat_message(self, message: str):
        """Add a message to the combat log.

        Args:
            message: Combat message
        """
        self._combat_log_lines.append(message)

        # Trim if needed
        if len(self._combat_log_lines) > self._max_combat_log_lines:
            self._combat_log_lines = self._combat_log_lines[-self._max_combat_log_lines:]

        # Update display
        self.combat_log.setPlainText("\n".join(self._combat_log_lines))

        # Auto-scroll to bottom
        scrollbar = self.combat_log.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def update_statistic(self, name: str, value: Any, is_percentage: bool = False):
        """Update a statistic value.

        Args:
            name: Statistic name
            value: Statistic value
            is_percentage: Whether to display as percentage
        """
        self.statistics_display.update_stat(name, value, is_percentage)

    def update_floor_info(self, floor_number: int, floor_name: str, special_status: str = ""):
        """Update the floor information display.

        Args:
            floor_number: Current floor number
            floor_name: Name of the floor
            special_status: Optional special status (e.g., "BOSS")
        """
        text = f"Floor {floor_number}: {floor_name}"
        if special_status:
            text += f" [{special_status}]"

        self.floor_info_label.setText(text)

        # Special styling for boss floors
        if special_status == "BOSS":
            self.floor_info_label.setStyleSheet(
                """
                QLabel {
                    background-color: #4b1a1a;
                    border: 2px solid #ff0000;
                    padding: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #ffaaaa;
                }
            """
            )

    def get_active_tab(self) -> str:
        """Get the name of the currently active tab.

        Returns:
            Name of the active tab
        """
        index = self.tab_widget.currentIndex()
        return self.tab_widget.tabText(index)
