"""Tests to ensure UI widgets maintain consistent interfaces.

These tests help prevent AttributeError issues by verifying that
all widgets have the expected attributes and methods.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from PyQt6.QtWidgets import QApplication, QLabel, QProgressBar, QListWidget

# Create QApplication for widget tests
app = QApplication([])

from client.widgets.character_panel import CharacterPanel
from client.widgets.info_panel import InfoPanel
from client.widgets.map_widget import MapWidget
from client.widgets.status_bar import StatusBar, MessagePriority


class TestCharacterPanelInterface:
    """Test CharacterPanel has the expected interface."""

    def test_basic_attributes(self):
        """Test basic widget attributes exist."""
        panel = CharacterPanel()

        # Labels
        assert hasattr(panel, "name_label")
        assert isinstance(panel.name_label, QLabel)

        # HP widgets
        assert hasattr(panel, "hp_bar")
        assert isinstance(panel.hp_bar, QProgressBar)
        assert hasattr(panel, "hp_label")
        assert isinstance(panel.hp_label, QLabel)

        # Stamina widgets
        assert hasattr(panel, "stamina_bar")
        assert isinstance(panel.stamina_bar, QProgressBar)
        assert hasattr(panel, "stamina_label")
        assert isinstance(panel.stamina_label, QLabel)

    def test_stats_labels(self):
        """Test stats labels dictionary."""
        panel = CharacterPanel()

        assert hasattr(panel, "stats_labels")
        assert isinstance(panel.stats_labels, dict)

        # Required stat keys
        required_stats = ["STR", "DEX", "INT", "VIT"]
        for stat in required_stats:
            assert stat in panel.stats_labels
            assert isinstance(panel.stats_labels[stat], QLabel)

    def test_list_widgets(self):
        """Test buff/debuff lists."""
        panel = CharacterPanel()

        assert hasattr(panel, "buffs_list")
        assert isinstance(panel.buffs_list, QListWidget)

        assert hasattr(panel, "debuffs_list")
        assert isinstance(panel.debuffs_list, QListWidget)

    def test_minimap(self):
        """Test minimap widget exists."""
        panel = CharacterPanel()

        # Note: actual widget uses 'minimap' not 'mini_map'
        assert hasattr(panel, "minimap")

    def test_action_slots(self):
        """Test action slot buttons."""
        panel = CharacterPanel()

        assert hasattr(panel, "action_slots")
        assert isinstance(panel.action_slots, dict)

        # Should have slots 1-9
        for i in range(1, 10):
            assert str(i) in panel.action_slots


class TestMapWidgetInterface:
    """Test MapWidget has the expected interface."""

    def test_attributes(self):
        """Test MapWidget attributes."""
        widget = MapWidget()

        assert hasattr(widget, "floor")
        assert hasattr(widget, "player_pos")
        assert hasattr(widget, "tile_size")
        assert hasattr(widget, "zoom_level")

    def test_methods(self):
        """Test MapWidget methods."""
        widget = MapWidget()

        assert hasattr(widget, "update")
        assert callable(widget.update)

        assert hasattr(widget, "zoom_in")
        assert callable(widget.zoom_in)

        assert hasattr(widget, "zoom_out")
        assert callable(widget.zoom_out)

    def test_zoom_functionality(self):
        """Test zoom actually changes zoom level."""
        widget = MapWidget()

        initial_zoom = widget.zoom_level
        widget.zoom_in()
        assert widget.zoom_level > initial_zoom

        widget.zoom_out()
        widget.zoom_out()
        assert widget.zoom_level < initial_zoom


class TestInfoPanelInterface:
    """Test InfoPanel has the expected interface."""

    def test_attributes(self):
        """Test InfoPanel attributes."""
        panel = InfoPanel()

        assert hasattr(panel, "tab_widget")
        assert hasattr(panel, "inventory_grid")
        assert hasattr(panel, "combat_log")
        assert hasattr(panel, "statistics_display")
        assert hasattr(panel, "floor_info_label")
        assert isinstance(panel.floor_info_label, QLabel)

    def test_methods(self):
        """Test InfoPanel methods."""
        panel = InfoPanel()

        # Combat log method
        assert hasattr(panel, "add_combat_message")
        assert callable(panel.add_combat_message)

        # Test adding a message
        panel.add_combat_message("Test message")
        assert "Test message" in panel.combat_log.toPlainText()

    def test_inventory_methods(self):
        """Test inventory-related methods."""
        panel = InfoPanel()

        assert hasattr(panel, "add_inventory_item")
        assert callable(panel.add_inventory_item)

        # Test signals
        assert hasattr(panel, "inventory_slot_clicked")


class TestStatusBarInterface:
    """Test StatusBar has the expected interface."""

    def test_methods(self):
        """Test StatusBar methods."""
        bar = StatusBar()

        assert hasattr(bar, "show_message")
        assert callable(bar.show_message)

    def test_message_priority_enum(self):
        """Test MessagePriority enum values."""
        assert hasattr(MessagePriority, "FLAVOR")
        assert hasattr(MessagePriority, "INFO")
        assert hasattr(MessagePriority, "COMBAT")

        assert MessagePriority.FLAVOR == 1
        assert MessagePriority.INFO == 2
        assert MessagePriority.COMBAT == 3

    def test_show_message(self):
        """Test showing messages."""
        bar = StatusBar()

        # Should not raise
        bar.show_message("Test", MessagePriority.INFO)
        bar.show_message("Combat!", MessagePriority.COMBAT, 5000)


def print_widget_interface(widget_class):
    """Helper to print all public attributes of a widget class."""
    widget = widget_class()

    print(f"\n{widget_class.__name__} Interface:")
    print("-" * 40)

    attrs = []
    for attr in dir(widget):
        if not attr.startswith("_") and not attr.startswith("qt_"):
            obj = getattr(widget, attr)
            if not callable(obj) or attr in ["update", "show_message", "zoom_in", "zoom_out"]:
                attrs.append((attr, type(obj).__name__))

    attrs.sort()
    for attr, type_name in attrs:
        print(f"  {attr}: {type_name}")


if __name__ == "__main__":
    # Print interface documentation
    print_widget_interface(CharacterPanel)
    print_widget_interface(MapWidget)
    print_widget_interface(InfoPanel)
    print_widget_interface(StatusBar)
