"""Demonstration script showing all panels working together."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from client.main_window import MainWindow
from client.widgets.status_bar import MessagePriority
from src.models.character import Character
from src.models.floor import Floor
from src.enums import TileType


def demo_panels():
    """Demonstrate all panels working together."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Create a test character
    character = Character("Valora", (5, 5))
    character.stamina = 75
    character.stamina_max = 100
    
    # Add attributes for display
    character.level = 5
    character.current_hp = 85
    character.max_hp = 100
    character.str_stat = 12
    character.dex_stat = 14
    character.int_stat = 10
    character.vit_stat = 11
    character.buffs = ["Blessed", "Swift"]
    character.debuffs = ["Poisoned"]
    
    # Create a test floor
    floor = Floor(20, 20, 1)
    floor.grid = [[TileType.FLOOR for _ in range(20)] for _ in range(20)]
    
    # Add some walls
    for i in range(20):
        floor.grid[0][i] = TileType.WALL
        floor.grid[19][i] = TileType.WALL
        floor.grid[i][0] = TileType.WALL
        floor.grid[i][19] = TileType.WALL
    
    # Set up the window
    window.set_floor(floor)
    window.set_player_position(5, 5)
    window.update_character(character)
    window.update_floor_info(1, "Starting Area")
    
    # Initial messages
    window.show_status_message("Welcome to Ascendant!", MessagePriority.INFO)
    window.add_combat_message("You enter the Eternal Spire...")
    
    # Add some statistics
    window.update_statistic("Floors Explored", 1)
    window.update_statistic("Enemies Killed", 0)
    window.update_statistic("Items Found", 0)
    window.update_statistic("Deaths", 0)
    window.update_statistic("Accuracy", 95.5, is_percentage=True)
    
    # Connect handlers
    def handle_action_slot(slot: int):
        window.show_status_message(f"Action slot {slot} clicked!", MessagePriority.INFO)
    
    def handle_inventory_slot(slot: int):
        window.show_status_message(f"Inventory slot {slot} clicked!", MessagePriority.INFO)
    
    window.connect_action_slots(handle_action_slot)
    window.connect_inventory_slots(handle_inventory_slot)
    
    # Simulate some updates
    def simulate_movement():
        """Simulate player movement."""
        current_pos = getattr(simulate_movement, 'pos', 5)
        current_pos += 1
        if current_pos > 15:
            current_pos = 5
        simulate_movement.pos = current_pos
        
        window.set_player_position(current_pos, 5)
        window.show_status_message(f"Moved to ({current_pos}, 5)", MessagePriority.FLAVOR)
    
    def simulate_combat():
        """Simulate combat message."""
        messages = [
            "You strike the goblin for 15 damage!",
            "The goblin attacks! You dodge.",
            "Critical hit! 30 damage!",
            "You found a health potion!"
        ]
        
        import random
        msg = random.choice(messages)
        window.add_combat_message(msg)
        
        # Update stats
        kills = getattr(simulate_combat, 'kills', 0)
        kills += 1
        simulate_combat.kills = kills
        window.update_statistic("Enemies Killed", kills)
    
    def simulate_damage():
        """Simulate taking damage."""
        if hasattr(character, 'current_hp'):
            character.current_hp = max(1, character.current_hp - 10)
            window.update_character(character)
            window.show_status_message("You take 10 damage!", MessagePriority.COMBAT)
    
    def simulate_floor_change():
        """Simulate changing floors."""
        floor_num = getattr(simulate_floor_change, 'floor', 1)
        floor_num += 1
        if floor_num > 10:
            floor_num = 1
        simulate_floor_change.floor = floor_num
        
        if floor_num % 5 == 0:
            window.update_floor_info(floor_num, f"Boss Arena", "BOSS")
            window.show_status_message("Boss floor reached!", MessagePriority.COMBAT)
        else:
            window.update_floor_info(floor_num, f"Floor {floor_num}")
            window.show_status_message(f"Entered floor {floor_num}", MessagePriority.INFO)
        
        window.update_statistic("Floors Explored", floor_num)
    
    # Set up timers for simulation
    movement_timer = QTimer()
    movement_timer.timeout.connect(simulate_movement)
    movement_timer.start(1000)  # Every second
    
    combat_timer = QTimer()
    combat_timer.timeout.connect(simulate_combat)
    combat_timer.start(3000)  # Every 3 seconds
    
    damage_timer = QTimer()
    damage_timer.timeout.connect(simulate_damage)
    damage_timer.start(5000)  # Every 5 seconds
    
    floor_timer = QTimer()
    floor_timer.timeout.connect(simulate_floor_change)
    floor_timer.start(10000)  # Every 10 seconds
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(demo_panels())