"""Character panel widget for displaying character information."""

from typing import Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.character import Character
from src.models.floor import Floor


class MiniMapWidget(QWidget):
    """Simple 10x10 mini-map display."""

    def __init__(self, parent=None):
        """Initialize the mini-map widget."""
        super().__init__(parent)
        self.grid_size = 10
        self.floor: Optional[Floor] = None
        self.player_pos: Optional[tuple] = None

        # Fixed size for mini-map
        self.setFixedSize(100, 100)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #555;")

    def paintEvent(self, event):
        """Paint the mini-map."""
        if not self.floor or not self.player_pos:
            return

        from PyQt6.QtGui import QPainter, QColor

        painter = QPainter(self)
        tile_size = self.width() // self.grid_size

        # Calculate viewport around player
        px, py = self.player_pos
        half_grid = self.grid_size // 2

        for dy in range(self.grid_size):
            for dx in range(self.grid_size):
                # Map grid position to world position
                wx = px - half_grid + dx
                wy = py - half_grid + dy

                # Draw tile if in bounds
                if 0 <= wx < self.floor.width and 0 <= wy < self.floor.height:
                    tile = self.floor.get_tile(wx, wy)
                    if tile:
                        # Choose color based on tile type
                        from src.enums import TileType

                        if tile.tile_type == TileType.WALL:
                            color = QColor(100, 100, 100)
                        else:
                            color = QColor(50, 50, 50)

                        painter.fillRect(
                            dx * tile_size, dy * tile_size, tile_size, tile_size, color
                        )

                # Draw player at center
                if dx == half_grid and dy == half_grid:
                    painter.fillRect(
                        dx * tile_size + 2,
                        dy * tile_size + 2,
                        tile_size - 4,
                        tile_size - 4,
                        QColor(0, 255, 0),
                    )


class CharacterPanel(QWidget):
    """Panel for displaying character information."""

    # Signal emitted when action slot is clicked
    action_slot_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize the character panel."""
        super().__init__(parent)

        # Create UI elements
        self._create_widgets()
        self._setup_layout()

        # Initialize with no character
        self.update_character(None)

    def _create_widgets(self):
        """Create all the widgets."""
        # Character name and portrait
        self.name_label = QLabel("No Character")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.portrait_placeholder = QLabel("Portrait")
        self.portrait_placeholder.setFixedSize(64, 64)
        self.portrait_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.portrait_placeholder.setStyleSheet("background-color: #333; border: 1px solid #555;")

        # HP/Stamina bars
        self.hp_bar = QProgressBar()
        self.hp_bar.setTextVisible(False)
        self.hp_label = QLabel("HP: 0/0")

        self.stamina_bar = QProgressBar()
        self.stamina_bar.setTextVisible(False)
        self.stamina_label = QLabel("Stamina: 0/0")

        # Stats display
        self.stats_labels: Dict[str, QLabel] = {}
        for stat in ["STR", "DEX", "INT", "VIT"]:
            self.stats_labels[stat] = QLabel(f"{stat}: 0")

        # Buffs/Debuffs lists
        self.buffs_list = QListWidget()
        self.buffs_list.setMaximumHeight(60)
        self.debuffs_list = QListWidget()
        self.debuffs_list.setMaximumHeight(60)

        # Mini-map
        self.minimap = MiniMapWidget()

        # Action slots
        self.action_slots: Dict[str, QPushButton] = {}
        for i in range(1, 10):
            btn = QPushButton(str(i))
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, num=i: self.action_slot_clicked.emit(num))
            self.action_slots[str(i)] = btn

    def _setup_layout(self):
        """Set up the widget layout."""
        layout = QVBoxLayout(self)

        # Character info section
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.portrait_placeholder)
        info_layout.addWidget(self.name_label, 1)
        layout.addLayout(info_layout)

        # HP/Stamina section
        hp_layout = QVBoxLayout()
        hp_layout.addWidget(self.hp_label)
        hp_layout.addWidget(self.hp_bar)
        layout.addLayout(hp_layout)

        stamina_layout = QVBoxLayout()
        stamina_layout.addWidget(self.stamina_label)
        stamina_layout.addWidget(self.stamina_bar)
        layout.addLayout(stamina_layout)

        # Stats section
        stats_group = QGroupBox("Stats")
        stats_layout = QGridLayout(stats_group)
        for i, (_stat, label) in enumerate(self.stats_labels.items()):
            stats_layout.addWidget(label, i // 2, i % 2)
        layout.addWidget(stats_group)

        # Buffs/Debuffs section
        buffs_group = QGroupBox("Buffs")
        buffs_layout = QVBoxLayout(buffs_group)
        buffs_layout.addWidget(self.buffs_list)
        layout.addWidget(buffs_group)

        debuffs_group = QGroupBox("Debuffs")
        debuffs_layout = QVBoxLayout(debuffs_group)
        debuffs_layout.addWidget(self.debuffs_list)
        layout.addWidget(debuffs_group)

        # Mini-map
        minimap_group = QGroupBox("Mini-Map")
        minimap_layout = QVBoxLayout(minimap_group)
        minimap_layout.addWidget(self.minimap)
        layout.addWidget(minimap_group)

        # Action slots
        slots_group = QGroupBox("Quick Actions")
        slots_layout = QGridLayout(slots_group)
        for i in range(9):
            row = i // 3
            col = i % 3
            slots_layout.addWidget(self.action_slots[str(i + 1)], row, col)
        layout.addWidget(slots_group)

        # Add stretch to push everything to top
        layout.addStretch()

    def update_character(self, character: Optional[Character]) -> None:
        """Update the panel with character data.

        Args:
            character: Character to display, or None
        """
        if character is None:
            self.name_label.setText("No Character")
            self.hp_bar.setValue(0)
            self.hp_bar.setMaximum(100)
            self.stamina_bar.setValue(0)
            self.stamina_bar.setMaximum(100)
            self.hp_label.setText("HP: 0/0")
            self.stamina_label.setText("Stamina: 0/0")

            for label in self.stats_labels.values():
                label.setText(label.text().split(":")[0] + ": 0")

            self.buffs_list.clear()
            self.debuffs_list.clear()
            return

        # Update name with level if available
        level_text = f" (Lv.{character.level})" if hasattr(character, "level") else ""
        self.name_label.setText(f"{character.name}{level_text}")

        # Update HP bar
        if hasattr(character, "current_hp") and hasattr(character, "max_hp"):
            self.hp_bar.setMaximum(character.max_hp)
            self.hp_bar.setValue(character.current_hp)
            self.hp_label.setText(f"HP: {character.current_hp}/{character.max_hp}")

            # Color based on percentage
            percentage = (
                (character.current_hp / character.max_hp) * 100 if character.max_hp > 0 else 0
            )
            if percentage > 50:
                color = "#00ff00"  # Green
            elif percentage > 25:
                color = "#ffff00"  # Yellow
            else:
                color = "#ff0000"  # Red

            self.hp_bar.setStyleSheet(
                f"""
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """
            )

        # Update stamina bar
        self.stamina_bar.setMaximum(character.stamina_max)
        self.stamina_bar.setValue(character.stamina)
        self.stamina_label.setText(f"Stamina: {character.stamina}/{character.stamina_max}")

        # Update stats
        for stat in ["STR", "DEX", "INT", "VIT"]:
            attr_name = f"{stat.lower()}_stat"
            if hasattr(character, attr_name):
                value = getattr(character, attr_name)
                self.stats_labels[stat].setText(f"{stat}: {value}")

        # Update buffs/debuffs
        self.buffs_list.clear()
        if hasattr(character, "buffs"):
            self.buffs_list.addItems(character.buffs)

        self.debuffs_list.clear()
        if hasattr(character, "debuffs"):
            self.debuffs_list.addItems(character.debuffs)

    def update_minimap(self, floor: Floor, player_pos: tuple) -> None:
        """Update the mini-map display.

        Args:
            floor: Current floor
            player_pos: Player position (x, y)
        """
        self.minimap.floor = floor
        self.minimap.player_pos = player_pos
        self.minimap.update()
