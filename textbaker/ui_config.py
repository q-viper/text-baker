"""
UI configuration constants for TextBaker.

This module contains all UI-related constants to avoid magic numbers
throughout the codebase. Modify these values to customize the UI appearance.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HandleConfig:
    """Configuration for graphics item handles."""

    # Rotation handle
    rotation_handle_size: int = 40
    rotation_handle_color: tuple = (0, 150, 255, 180)  # RGBA
    rotation_handle_border_color: tuple = (255, 255, 255, 255)
    rotation_handle_border_width: int = 3
    rotation_handle_active_color: tuple = (76, 175, 80, 200)

    # Resize handles (corner handles)
    resize_handle_size: int = 20
    resize_handle_color: tuple = (255, 150, 0, 200)  # Orange RGBA
    resize_handle_border_color: tuple = (255, 255, 255, 255)
    resize_handle_border_width: int = 2

    # Selection border
    border_color: tuple = (0, 150, 255, 255)
    border_width: int = 2
    border_active_color: tuple = (76, 175, 80, 255)

    # Minimum size constraints
    min_resize_width: int = 20
    min_resize_height: int = 20


@dataclass(frozen=True)
class ZoomConfig:
    """Configuration for zoom behavior."""

    zoom_in_factor: float = 1.15
    min_zoom: float = 0.1
    max_zoom: float = 10.0


@dataclass(frozen=True)
class IconConfig:
    """Configuration for icon generation."""

    # Icon sizes to generate
    sizes: tuple = (256, 128, 64, 48, 32, 16)

    # Bread/toast colors (BGRA for OpenCV)
    bread_color: tuple = (70, 175, 245, 255)
    bread_light_color: tuple = (120, 210, 255, 255)
    crust_color: tuple = (40, 130, 200, 255)

    # Text colors
    text_color: tuple = (50, 50, 80, 255)
    text_shadow_color: tuple = (30, 80, 120, 200)

    # Detail thresholds
    min_size_for_ellipse: int = 48
    min_size_for_inner: int = 64
    min_size_for_shadow: int = 48
    min_size_for_texture: int = 128


# Global instances for easy import
HANDLE_CONFIG = HandleConfig()
ZOOM_CONFIG = ZoomConfig()
ICON_CONFIG = IconConfig()
