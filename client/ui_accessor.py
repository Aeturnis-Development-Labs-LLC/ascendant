"""Type-safe UI accessor to prevent attribute errors.

This module provides a safe way to access UI elements with proper
error handling and attribute validation.
"""

from typing import Any, Optional, TypeVar, Union

from PyQt6.QtWidgets import QLabel, QProgressBar, QWidget

T = TypeVar('T')


class UIAccessor:
    """Safe accessor for UI widgets with attribute validation."""
    
    def __init__(self, widget: Optional[QWidget] = None):
        """Initialize with optional widget."""
        self._widget = widget
    
    def set_widget(self, widget: QWidget) -> None:
        """Set the widget to access."""
        self._widget = widget
    
    def get_attr(self, attr_name: str, default: T = None) -> Union[Any, T]:
        """Safely get an attribute from the widget.
        
        Args:
            attr_name: Name of the attribute
            default: Default value if attribute doesn't exist
            
        Returns:
            The attribute value or default
        """
        if not self._widget:
            return default
        
        return getattr(self._widget, attr_name, default)
    
    def set_text(self, attr_name: str, text: str) -> bool:
        """Safely set text on a label.
        
        Args:
            attr_name: Name of the label attribute
            text: Text to set
            
        Returns:
            True if successful
        """
        label = self.get_attr(attr_name)
        if isinstance(label, QLabel):
            label.setText(text)
            return True
        return False
    
    def set_progress(self, bar_name: str, value: int, maximum: int = 100) -> bool:
        """Safely set progress bar value.
        
        Args:
            bar_name: Name of the progress bar attribute
            value: Current value
            maximum: Maximum value
            
        Returns:
            True if successful
        """
        bar = self.get_attr(bar_name)
        if isinstance(bar, QProgressBar):
            bar.setMaximum(maximum)
            bar.setValue(value)
            return True
        return False
    
    def has_attr(self, attr_name: str) -> bool:
        """Check if widget has an attribute.
        
        Args:
            attr_name: Name of the attribute
            
        Returns:
            True if attribute exists
        """
        return self._widget is not None and hasattr(self._widget, attr_name)
    
    def validate_interface(self, required_attrs: list[str]) -> list[str]:
        """Validate widget has required attributes.
        
        Args:
            required_attrs: List of required attribute names
            
        Returns:
            List of missing attributes
        """
        if not self._widget:
            return required_attrs
        
        missing = []
        for attr in required_attrs:
            if not hasattr(self._widget, attr):
                missing.append(attr)
        
        return missing


class SafeCharacterPanel:
    """Type-safe wrapper for CharacterPanel."""
    
    REQUIRED_ATTRS = [
        'name_label', 'hp_bar', 'hp_label', 
        'stamina_bar', 'stamina_label', 'stats_labels',
        'buffs_list', 'debuffs_list', 'minimap'
    ]
    
    def __init__(self, panel: Optional[QWidget] = None):
        """Initialize with optional panel."""
        self._accessor = UIAccessor(panel)
    
    def update_name(self, name: str) -> bool:
        """Update character name display."""
        return self._accessor.set_text('name_label', f"Name: {name}")
    
    def update_hp(self, current: int, maximum: int) -> bool:
        """Update HP bar and label."""
        success = self._accessor.set_progress('hp_bar', current, maximum)
        success &= self._accessor.set_text('hp_label', f"HP: {current}/{maximum}")
        return success
    
    def update_stamina(self, current: int, maximum: int) -> bool:
        """Update stamina bar and label."""
        success = self._accessor.set_progress('stamina_bar', current, maximum)
        success &= self._accessor.set_text('stamina_label', f"Stamina: {current}/{maximum}")
        return success
    
    def update_stat(self, stat_name: str, value: Any) -> bool:
        """Update a stat label."""
        stats_dict = self._accessor.get_attr('stats_labels', {})
        if stat_name in stats_dict and isinstance(stats_dict[stat_name], QLabel):
            stats_dict[stat_name].setText(f"{stat_name}: {value}")
            return True
        return False
    
    def validate(self) -> list[str]:
        """Validate the panel has required attributes."""
        return self._accessor.validate_interface(self.REQUIRED_ATTRS)


class SafeMapWidget:
    """Type-safe wrapper for MapWidget."""
    
    REQUIRED_ATTRS = [
        'floor', 'player_pos', 'tile_size', 'zoom_level',
        'update', 'zoom_in', 'zoom_out'
    ]
    
    def __init__(self, widget: Optional[QWidget] = None):
        """Initialize with optional widget."""
        self._widget = widget
        self._accessor = UIAccessor(widget)
    
    def set_floor(self, floor: Any) -> bool:
        """Set the floor data."""
        if self._widget and hasattr(self._widget, 'floor'):
            self._widget.floor = floor
            return True
        return False
    
    def set_player_pos(self, x: int, y: int) -> bool:
        """Set player position."""
        if self._widget and hasattr(self._widget, 'player_pos'):
            self._widget.player_pos = (x, y)
            return True
        return False
    
    def update_display(self) -> bool:
        """Update the map display."""
        if self._widget and hasattr(self._widget, 'update'):
            self._widget.update()
            return True
        return False
    
    def validate(self) -> list[str]:
        """Validate the widget has required attributes."""
        return self._accessor.validate_interface(self.REQUIRED_ATTRS)


# Example usage:
def safe_update_ui(window):
    """Example of safely updating UI without AttributeErrors."""
    # Create safe accessors
    char_panel = SafeCharacterPanel(window.character_panel)
    map_widget = SafeMapWidget(window.map_widget)
    
    # Validate interfaces
    char_missing = char_panel.validate()
    if char_missing:
        print(f"CharacterPanel missing: {char_missing}")
    
    map_missing = map_widget.validate()
    if map_missing:
        print(f"MapWidget missing: {map_missing}")
    
    # Safe updates - won't crash if attributes missing
    char_panel.update_name("Hero")
    char_panel.update_hp(80, 100)
    char_panel.update_stamina(75, 100)
    char_panel.update_stat("STR", 15)
    
    map_widget.set_player_pos(10, 10)
    map_widget.update_display()