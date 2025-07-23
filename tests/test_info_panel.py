"""Tests for info panel widget - UTF Contract GAME-UI-003."""

import sys
from unittest.mock import MagicMock

import pytest

try:
    from PyQt6.QtWidgets import QApplication, QTabWidget, QWidget

    from client.widgets.info_panel import InfoPanel

    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QApplication = None
    QWidget = None
    QTabWidget = None
    InfoPanel = None

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
def info_panel(qapp):
    """Create an InfoPanel instance for testing."""
    panel = InfoPanel()
    yield panel
    panel.close()


class TestInfoPanelStructure:
    """Test info panel structure and initialization."""

    def test_panel_creation(self, info_panel):
        """Test panel is created with correct structure."""
        assert isinstance(info_panel, QWidget)
        assert hasattr(info_panel, "tab_widget")
        assert hasattr(info_panel, "floor_info_label")
        assert hasattr(info_panel, "inventory_grid")
        assert hasattr(info_panel, "combat_log")
        assert hasattr(info_panel, "statistics_display")

    def test_tab_structure(self, info_panel):
        """Test tabs are created correctly."""
        tab_widget = info_panel.tab_widget
        assert isinstance(tab_widget, QTabWidget)
        assert tab_widget.count() == 3

        # Check tab names
        assert tab_widget.tabText(0) == "Inventory"
        assert tab_widget.tabText(1) == "Combat Log"
        assert tab_widget.tabText(2) == "Statistics"

    def test_floor_info_always_visible(self, info_panel):
        """Test floor info is outside tabs and always visible."""
        # Floor info should not be in any tab
        assert info_panel.floor_info_label.parent() != info_panel.tab_widget
        # Check it's in the main layout
        layout = info_panel.layout()
        assert layout is not None
        # Check the label exists and has default text
        assert info_panel.floor_info_label.text() == "Floor 1: Starting Area"


class TestInventoryTab:
    """Test inventory tab functionality."""

    def test_inventory_grid_layout(self, info_panel):
        """Test inventory has grid layout."""
        inventory = info_panel.inventory_grid
        assert inventory is not None
        assert hasattr(inventory, "add_item")
        assert hasattr(inventory, "remove_item")
        assert hasattr(inventory, "clear_items")

    def test_add_items_to_inventory(self, info_panel):
        """Test adding items to inventory grid."""
        # Mock item
        item = MagicMock()
        item.name = "Health Potion"
        item.icon = "potion.png"

        info_panel.add_inventory_item(item, slot=0)

        # Check item was added
        assert info_panel.inventory_grid.get_item(0) == item

    def test_inventory_slot_signals(self, info_panel):
        """Test inventory slots emit signals when clicked."""
        slot_clicked = False
        clicked_slot = -1

        def on_slot_click(slot):
            nonlocal slot_clicked, clicked_slot
            slot_clicked = True
            clicked_slot = slot

        info_panel.inventory_slot_clicked.connect(on_slot_click)
        info_panel.inventory_grid.click_slot(0)

        assert slot_clicked
        assert clicked_slot == 0


class TestCombatLogTab:
    """Test combat log functionality."""

    def test_combat_log_display(self, info_panel):
        """Test combat log can display messages."""
        info_panel.add_combat_message("Player attacks Goblin for 10 damage!")
        info_panel.add_combat_message("Goblin attacks Player for 5 damage!")

        log_text = info_panel.combat_log.toPlainText()
        assert "Player attacks Goblin for 10 damage!" in log_text
        assert "Goblin attacks Player for 5 damage!" in log_text

    def test_combat_log_scrolling(self, info_panel):
        """Test combat log auto-scrolls to bottom."""
        # Add many messages
        for i in range(100):
            info_panel.add_combat_message(f"Message {i}")

        # Should be scrolled to bottom
        scrollbar = info_panel.combat_log.verticalScrollBar()
        assert scrollbar.value() == scrollbar.maximum()

    def test_combat_log_max_lines(self, info_panel):
        """Test combat log has maximum line limit."""
        # Add many messages
        for i in range(1000):
            info_panel.add_combat_message(f"Message {i}")

        # Should not exceed max lines (e.g., 500)
        lines = info_panel.combat_log.toPlainText().split("\n")
        assert len(lines) <= 500


class TestStatisticsTab:
    """Test statistics display functionality."""

    def test_statistics_categories(self, info_panel):
        """Test statistics display has categories."""
        stats = info_panel.statistics_display
        assert hasattr(stats, "update_stat")

        # Common statistics categories
        categories = ["Combat", "Exploration", "Items", "Deaths"]
        for category in categories:
            assert category in stats.get_categories()

    def test_update_statistics(self, info_panel):
        """Test updating statistics values."""
        info_panel.update_statistic("Enemies Killed", 42)
        info_panel.update_statistic("Floors Explored", 7)
        info_panel.update_statistic("Items Found", 23)

        stats_text = info_panel.statistics_display.toPlainText()
        assert "Enemies Killed: 42" in stats_text
        assert "Floors Explored: 7" in stats_text
        assert "Items Found: 23" in stats_text

    def test_percentage_calculations(self, info_panel):
        """Test statistics can show percentages."""
        info_panel.update_statistic("Hit Rate", 85, is_percentage=True)
        info_panel.update_statistic("Critical Rate", 15.5, is_percentage=True)

        stats_text = info_panel.statistics_display.toPlainText()
        assert "Hit Rate: 85%" in stats_text
        assert "Critical Rate: 15.5%" in stats_text


class TestFloorInfo:
    """Test floor information display."""

    def test_floor_info_update(self, info_panel):
        """Test updating floor information."""
        info_panel.update_floor_info(floor_number=5, floor_name="Goblin Warren")

        assert "Floor 5" in info_panel.floor_info_label.text()
        assert "Goblin Warren" in info_panel.floor_info_label.text()

    def test_floor_special_status(self, info_panel):
        """Test displaying special floor status."""
        info_panel.update_floor_info(
            floor_number=10, floor_name="Boss Chamber", special_status="BOSS"
        )

        text = info_panel.floor_info_label.text()
        assert "Floor 10" in text
        assert "Boss Chamber" in text
        assert "BOSS" in text


class TestTabStateMaintenance:
    """Test maintaining state during tab switches."""

    def test_tab_switch_preserves_content(self, info_panel):
        """Test content is preserved when switching tabs."""
        # Add content to each tab
        item = MagicMock()
        item.name = "Sword"
        info_panel.add_inventory_item(item, 0)
        info_panel.add_combat_message("Test message")
        info_panel.update_statistic("Test Stat", 100)

        # Switch through tabs
        for i in range(3):
            info_panel.tab_widget.setCurrentIndex(i)

        # Go back to first tab and check content
        info_panel.tab_widget.setCurrentIndex(0)
        assert info_panel.inventory_grid.get_item(0) == item

        info_panel.tab_widget.setCurrentIndex(1)
        assert "Test message" in info_panel.combat_log.toPlainText()

        info_panel.tab_widget.setCurrentIndex(2)
        assert "Test Stat: 100" in info_panel.statistics_display.toPlainText()

    def test_active_tab_tracking(self, info_panel):
        """Test panel tracks which tab is active."""
        info_panel.tab_widget.setCurrentIndex(1)
        assert info_panel.get_active_tab() == "Combat Log"

        info_panel.tab_widget.setCurrentIndex(0)
        assert info_panel.get_active_tab() == "Inventory"
