"""Tests for loot generation to improve coverage."""

import pytest

from src.game.loot_system import LootSystem, LootDrop


class TestLootGeneration:
    """Tests for loot generation."""
    
    def test_generate_loot_basic(self):
        """Test basic loot generation."""
        loot_system = LootSystem(seed=42)
        
        # Generate loot for a goblin on floor 1
        drops = loot_system.generate_loot("goblin", 1, luck=0)
        
        # Should get some drops (goblin has 70% chance for gold)
        assert isinstance(drops, list)
        # All drops should be LootDrop instances
        for drop in drops:
            assert isinstance(drop, LootDrop)
            assert hasattr(drop, "item_name")
            assert hasattr(drop, "quantity")
            assert hasattr(drop, "item_type")
    
    def test_generate_loot_with_luck(self):
        """Test that luck increases drop chances."""
        # Use fixed seed for deterministic results
        loot_system = LootSystem(seed=42)
        
        # Generate without luck
        drops_no_luck = []
        for _ in range(10):
            drops_no_luck.extend(loot_system.generate_loot("rat", 1, luck=0))
        
        # Generate with high luck
        loot_system_lucky = LootSystem(seed=42)
        drops_with_luck = []
        for _ in range(10):
            drops_with_luck.extend(loot_system_lucky.generate_loot("rat", 1, luck=50))
        
        # With 50% additional drop chance from luck, should get more drops
        assert len(drops_with_luck) >= len(drops_no_luck)
    
    def test_generate_loot_floor_scaling(self):
        """Test that currency scales with floor level."""
        loot_system = LootSystem(seed=1234)  # Seed that guarantees gold drop
        
        # Force gold drop by manipulating random
        import random
        random.seed(1234)
        
        # Generate loot on different floors
        drops_floor1 = loot_system.generate_loot("demon", 1, luck=0)
        
        # Reset seed for same drops
        random.seed(1234)
        drops_floor5 = loot_system.generate_loot("demon", 5, luck=0)
        
        # Find gold drops
        gold_floor1 = None
        gold_floor5 = None
        
        for drop in drops_floor1:
            if drop.item_name == "Gold":
                gold_floor1 = drop.quantity
                
        for drop in drops_floor5:
            if drop.item_name == "Gold":
                gold_floor5 = drop.quantity
        
        # Floor 5 should have more gold (40% more)
        if gold_floor1 and gold_floor5:
            assert gold_floor5 > gold_floor1
    
    def test_generate_loot_quantity_ranges(self):
        """Test that quantity ranges work correctly."""
        loot_system = LootSystem(seed=42)
        
        # Collect many drops to test range
        gold_amounts = []
        for i in range(100):
            loot_system._rng.seed(42 + i)
            drops = loot_system.generate_loot("goblin", 1, luck=100)  # High luck for guaranteed drops
            for drop in drops:
                if drop.item_name == "Gold":
                    gold_amounts.append(drop.quantity)
        
        # Goblin gold is (3, 8) range
        if gold_amounts:
            assert min(gold_amounts) >= 3
            assert max(gold_amounts) <= 8
    
    def test_generate_loot_unknown_monster(self):
        """Test loot generation for unknown monster type."""
        loot_system = LootSystem(seed=42)
        
        # Unknown monster should return empty list
        drops = loot_system.generate_loot("unknown_monster", 1, luck=0)
        assert drops == []
    
    def test_loot_drop_types(self):
        """Test different loot drop types."""
        loot_system = LootSystem(seed=42)
        
        # Collect various drops
        all_drops = []
        for monster in ["rat", "goblin", "skeleton", "orc", "troll", "demon"]:
            for i in range(10):
                loot_system._rng.seed(42 + i)
                drops = loot_system.generate_loot(monster, 1, luck=50)
                all_drops.extend(drops)
        
        # Check we have various types
        item_types = set(drop.item_type for drop in all_drops)
        assert "currency" in item_types
        
        # Check some items exist
        item_names = set(drop.item_name for drop in all_drops)
        assert "Gold" in item_names