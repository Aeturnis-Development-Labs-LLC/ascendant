"""Tests for character panel widget - UTF Contract GAME-UI-003."""

import sys
from unittest.mock import MagicMock

import pytest

try:
    from PyQt6.QtWidgets import QApplication, QWidget

    from client.widgets.character_panel import CharacterPanel
    from src.models.character import Character

    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QApplication = None
    QWidget = None
    CharacterPanel = None
    Character = None

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
def character():
    """Create a test character with extended attributes."""
    char = Character("Test Hero", 10, 10)
    # Add attributes needed for display
    char.current_hp = 80
    char.max_hp = 100
    char.level = 5
    char.str_stat = 15
    char.dex_stat = 12
    char.int_stat = 10
    char.vit_stat = 14
    char.buffs = ["Strength+", "Shield"]
    char.debuffs = ["Poison"]
    return char


@pytest.fixture
def character_panel(qapp):
    """Create a CharacterPanel instance for testing."""
    panel = CharacterPanel()
    yield panel
    panel.close()


class TestCharacterPanelInitialization:
    """Test character panel initialization."""

    def test_panel_creation(self, character_panel):
        """Test panel is created with correct structure."""
        assert isinstance(character_panel, QWidget)
        assert hasattr(character_panel, "name_label")
        assert hasattr(character_panel, "hp_bar")
        assert hasattr(character_panel, "stamina_bar")
        assert hasattr(character_panel, "stats_labels")
        assert hasattr(character_panel, "buffs_list")
        assert hasattr(character_panel, "debuffs_list")
        assert hasattr(character_panel, "action_slots")

    def test_default_state(self, character_panel):
        """Test panel has correct default state."""
        assert character_panel.name_label.text() == "No Character"
        assert character_panel.hp_bar.value() == 0
        assert character_panel.stamina_bar.value() == 0
        assert len(character_panel.stats_labels) == 4  # STR, DEX, INT, VIT
        assert len(character_panel.action_slots) == 9  # Slots 1-9


class TestCharacterDisplay:
    """Test character information display."""

    def test_update_character_info(self, character_panel, character):
        """Test updating panel with character data."""
        character_panel.update_character(character)

        assert character_panel.name_label.text() == "Test Hero (Lv.5)"
        assert character_panel.hp_bar.value() == 80
        assert character_panel.hp_bar.maximum() == 100
        assert character_panel.stamina_bar.value() == 100
        assert character_panel.stamina_bar.maximum() == 100

    def test_stats_display(self, character_panel, character):
        """Test stats are displayed correctly."""
        character_panel.update_character(character)

        assert "STR: 15" in character_panel.stats_labels["STR"].text()
        assert "DEX: 12" in character_panel.stats_labels["DEX"].text()
        assert "INT: 10" in character_panel.stats_labels["INT"].text()
        assert "VIT: 14" in character_panel.stats_labels["VIT"].text()

    def test_buffs_debuffs_display(self, character_panel, character):
        """Test buffs and debuffs are shown."""
        character_panel.update_character(character)

        # Check buffs
        buff_texts = [
            character_panel.buffs_list.item(i).text()
            for i in range(character_panel.buffs_list.count())
        ]
        assert "Strength+" in buff_texts
        assert "Shield" in buff_texts

        # Check debuffs
        debuff_texts = [
            character_panel.debuffs_list.item(i).text()
            for i in range(character_panel.debuffs_list.count())
        ]
        assert "Poison" in debuff_texts


class TestHealthStaminaBars:
    """Test HP and stamina bar functionality."""

    def test_hp_bar_colors(self, character_panel, character):
        """Test HP bar changes color based on percentage."""
        # Full HP - should be green
        character.current_hp = 100
        character_panel.update_character(character)
        style = character_panel.hp_bar.styleSheet()
        assert "green" in style or "#00ff00" in style

        # Half HP - should be yellow
        character.current_hp = 50
        character_panel.update_character(character)
        style = character_panel.hp_bar.styleSheet()
        assert "yellow" in style or "#ffff00" in style

        # Low HP - should be red
        character.current_hp = 20
        character_panel.update_character(character)
        style = character_panel.hp_bar.styleSheet()
        assert "red" in style or "#ff0000" in style

    def test_bar_labels(self, character_panel, character):
        """Test bars show numeric values."""
        character_panel.update_character(character)

        assert character_panel.hp_label.text() == "HP: 80/100"
        assert character_panel.stamina_label.text() == "Stamina: 100/100"


class TestActionSlots:
    """Test quick action slot functionality."""

    def test_action_slot_count(self, character_panel):
        """Test correct number of action slots."""
        assert len(character_panel.action_slots) == 9
        for i in range(9):
            assert str(i + 1) in character_panel.action_slots

    def test_action_slot_signals(self, character_panel):
        """Test action slots emit signals when clicked."""
        slot_clicked = False
        slot_number = 0

        def on_slot_click(num):
            nonlocal slot_clicked, slot_number
            slot_clicked = True
            slot_number = num

        character_panel.action_slot_clicked.connect(on_slot_click)
        character_panel.action_slots["1"].click()

        assert slot_clicked
        assert slot_number == 1


class TestPanelUpdates:
    """Test panel update behavior."""

    def test_real_time_updates(self, character_panel, character):
        """Test panel updates immediately on state change."""
        character_panel.update_character(character)

        # Change HP
        character.current_hp = 50
        character_panel.update_character(character)
        assert character_panel.hp_bar.value() == 50

        # Change stamina
        character.stamina = 75
        character_panel.update_character(character)
        assert character_panel.stamina_bar.value() == 75

    def test_null_character_handling(self, character_panel):
        """Test panel handles null character gracefully."""
        character_panel.update_character(None)

        assert character_panel.name_label.text() == "No Character"
        assert character_panel.hp_bar.value() == 0
        assert character_panel.stamina_bar.value() == 0


class TestMiniMap:
    """Test mini-map functionality."""

    def test_minimap_exists(self, character_panel):
        """Test minimap widget exists."""
        assert hasattr(character_panel, "minimap")
        assert character_panel.minimap is not None

    def test_minimap_size(self, character_panel):
        """Test minimap has correct size."""
        # Should be 10x10 compressed view
        assert character_panel.minimap.grid_size == 10

    def test_minimap_update(self, character_panel):
        """Test minimap can be updated with floor data."""
        from src.models.floor import Floor

        floor = Floor(seed=42)
        floor.generate()

        character_panel.update_minimap(floor, (10, 10))
        # Minimap should have floor data
        assert character_panel.minimap.floor is not None
