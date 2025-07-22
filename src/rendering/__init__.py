"""Rendering package for ASCII color system."""

from src.rendering.color_scheme import ColorScheme, ColorMode
from src.rendering.color_effects import (
    apply_fog_of_war,
    apply_status_effect,
    flash_damage,
    brightness_adjust,
    StatusEffect,
    DamageType,
)
from src.rendering.accessibility import (
    ColorblindMode,
    apply_colorblind_filter,
    apply_high_contrast,
    get_enhanced_symbol,
    AccessibilityConfig,
)

__all__ = [
    "ColorScheme",
    "ColorMode",
    "apply_fog_of_war",
    "apply_status_effect",
    "flash_damage",
    "brightness_adjust",
    "StatusEffect",
    "DamageType",
    "ColorblindMode",
    "apply_colorblind_filter",
    "apply_high_contrast",
    "get_enhanced_symbol",
    "AccessibilityConfig",
]
