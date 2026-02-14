"""
Tests for the UI configuration module.
"""

import pytest

from textbaker.ui_config import (
    HANDLE_CONFIG,
    ICON_CONFIG,
    ZOOM_CONFIG,
    HandleConfig,
    IconConfig,
    ZoomConfig,
)


class TestHandleConfig:
    """Tests for HandleConfig."""

    def test_default_values(self):
        """Test default handle configuration values."""
        config = HandleConfig()

        assert config.rotation_handle_size == 40
        assert config.resize_handle_size == 20
        assert config.border_width == 2
        assert config.min_resize_width == 20
        assert config.min_resize_height == 20

    def test_color_tuples(self):
        """Test that color values are tuples."""
        config = HandleConfig()

        assert isinstance(config.rotation_handle_color, tuple)
        assert len(config.rotation_handle_color) == 4  # RGBA
        assert isinstance(config.resize_handle_color, tuple)
        assert len(config.resize_handle_color) == 4  # RGBA

    def test_frozen(self):
        """Test that config is immutable (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        config = HandleConfig()

        with pytest.raises(FrozenInstanceError):
            config.rotation_handle_size = 50


class TestZoomConfig:
    """Tests for ZoomConfig."""

    def test_default_values(self):
        """Test default zoom configuration values."""
        config = ZoomConfig()

        assert config.zoom_in_factor == 1.15
        assert config.min_zoom == 0.1
        assert config.max_zoom == 10.0

    def test_zoom_factor_positive(self):
        """Test that zoom factor is positive."""
        config = ZoomConfig()

        assert config.zoom_in_factor > 0
        assert config.min_zoom > 0
        assert config.max_zoom > config.min_zoom


class TestIconConfig:
    """Tests for IconConfig."""

    def test_default_sizes(self):
        """Test default icon sizes."""
        config = IconConfig()

        assert 256 in config.sizes
        assert 128 in config.sizes
        assert 64 in config.sizes
        assert 16 in config.sizes

    def test_color_tuples(self):
        """Test that color values are tuples."""
        config = IconConfig()

        assert isinstance(config.bread_color, tuple)
        assert isinstance(config.text_color, tuple)

    def test_size_thresholds(self):
        """Test size threshold values."""
        config = IconConfig()

        assert config.min_size_for_ellipse > 0
        assert config.min_size_for_inner >= config.min_size_for_ellipse
        assert config.min_size_for_texture >= config.min_size_for_inner


class TestGlobalInstances:
    """Tests for global config instances."""

    def test_handle_config_exists(self):
        """Test that HANDLE_CONFIG is available."""
        assert HANDLE_CONFIG is not None
        assert isinstance(HANDLE_CONFIG, HandleConfig)

    def test_zoom_config_exists(self):
        """Test that ZOOM_CONFIG is available."""
        assert ZOOM_CONFIG is not None
        assert isinstance(ZOOM_CONFIG, ZoomConfig)

    def test_icon_config_exists(self):
        """Test that ICON_CONFIG is available."""
        assert ICON_CONFIG is not None
        assert isinstance(ICON_CONFIG, IconConfig)
