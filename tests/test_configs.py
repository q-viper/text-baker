"""
Tests for configuration models.
"""

import json
from pathlib import Path

from textbaker.core.configs import (
    BackgroundConfig,
    CharacterConfig,
    ColorConfig,
    DatasetConfig,
    GeneratorConfig,
    OutputConfig,
    TextureConfig,
    TransformConfig,
)


class TestTransformConfig:
    """Tests for TransformConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TransformConfig()

        assert config.rotation_range == (0.0, 0.0)
        assert config.perspective_range == (0.0, 0.0)
        assert config.scale_range == (0.9, 1.1)
        assert config.shear_range == (0.0, 0.0)

    def test_custom_values(self):
        """Test custom configuration values."""
        config = TransformConfig(
            rotation_range=(-15, 15),
            perspective_range=(0.0, 0.1),
            scale_range=(0.8, 1.2),
            shear_range=(-5, 5),
        )

        assert config.rotation_range == (-15, 15)
        assert config.perspective_range == (0.0, 0.1)
        assert config.scale_range == (0.8, 1.2)
        assert config.shear_range == (-5, 5)

    def test_list_to_tuple_conversion(self):
        """Test that lists are converted to tuples."""
        config = TransformConfig(
            rotation_range=[-10, 10],
            scale_range=[0.9, 1.1],
        )

        assert isinstance(config.rotation_range, tuple)
        assert isinstance(config.scale_range, tuple)


class TestColorConfig:
    """Tests for ColorConfig."""

    def test_default_values(self):
        """Test default color configuration."""
        config = ColorConfig()

        assert config.random_color is False
        assert config.color_range_r == (0, 255)
        assert config.color_range_g == (0, 255)
        assert config.color_range_b == (0, 255)
        assert config.fixed_color is None

    def test_random_color_enabled(self):
        """Test random color configuration."""
        config = ColorConfig(
            random_color=True,
            color_range_r=(100, 200),
            color_range_g=(50, 150),
            color_range_b=(0, 100),
        )

        assert config.random_color is True
        assert config.color_range_r == (100, 200)

    def test_fixed_color(self):
        """Test fixed color configuration."""
        config = ColorConfig(
            fixed_color=(255, 0, 0),
        )

        assert config.fixed_color == (255, 0, 0)


class TestTextureConfig:
    """Tests for TextureConfig."""

    def test_default_values(self):
        """Test default texture configuration."""
        config = TextureConfig()

        assert config.enabled is False
        assert config.texture_dir is None
        assert config.per_character is False
        assert config.opacity == 1.0

    def test_enabled_with_dir(self):
        """Test enabled texture with directory."""
        config = TextureConfig(
            enabled=True,
            texture_dir=Path("./textures"),
            opacity=0.8,
        )

        assert config.enabled is True
        assert config.opacity == 0.8

    def test_opacity_bounds(self):
        """Test opacity validation."""
        # Valid opacity
        config = TextureConfig(opacity=0.5)
        assert config.opacity == 0.5

        # Edge cases
        config = TextureConfig(opacity=0.0)
        assert config.opacity == 0.0

        config = TextureConfig(opacity=1.0)
        assert config.opacity == 1.0


class TestBackgroundConfig:
    """Tests for BackgroundConfig."""

    def test_default_values(self):
        """Test default background configuration."""
        config = BackgroundConfig()

        assert config.enabled is False

    def test_with_directory(self):
        """Test background with directory."""
        config = BackgroundConfig(
            enabled=True,
            background_dir=Path("./backgrounds"),
        )

        assert config.enabled is True


class TestDatasetConfig:
    """Tests for DatasetConfig."""

    def test_default_values(self):
        """Test default dataset configuration."""
        config = DatasetConfig()

        assert config.recursive is True
        assert ".png" in config.extensions
        assert ".jpg" in config.extensions

    def test_custom_extensions(self):
        """Test custom extensions."""
        config = DatasetConfig(
            extensions=[".png", ".bmp"],
        )

        assert ".png" in config.extensions
        assert ".bmp" in config.extensions


class TestOutputConfig:
    """Tests for OutputConfig."""

    def test_default_values(self):
        """Test default output configuration."""
        config = OutputConfig()

        assert config.format == "png"
        assert config.create_labels is True
        assert config.crop_to_text is True

    def test_crop_to_text_parameter(self):
        """Test crop_to_text parameter."""
        config = OutputConfig(crop_to_text=False)

        assert config.crop_to_text is False


class TestGeneratorConfig:
    """Tests for GeneratorConfig."""

    def test_default_values(self):
        """Test default generator configuration."""
        config = GeneratorConfig()

        assert config.seed == 42
        assert config.spacing == 0
        assert config.text_length == (1, 10)
        assert config.canvas_height == 128
        assert config.max_v_offset == 20
        assert config.font_scale == 1.5

    def test_new_ui_parameters(self):
        """Test new UI parameters."""
        config = GeneratorConfig(
            canvas_height=200,
            max_v_offset=30,
            font_scale=2.0,
        )

        assert config.canvas_height == 200
        assert config.max_v_offset == 30
        assert config.font_scale == 2.0

    def test_nested_configs(self):
        """Test nested configuration objects."""
        config = GeneratorConfig(
            seed=123,
            transform=TransformConfig(rotation_range=(-10, 10)),
            color=ColorConfig(random_color=True),
        )

        assert config.seed == 123
        assert config.transform.rotation_range == (-10, 10)
        assert config.color.random_color is True

    def test_from_yaml_file(self, sample_config_yaml):
        """Test loading config from YAML file."""
        config = GeneratorConfig.from_file(sample_config_yaml)

        assert config.seed == 123
        assert config.spacing == 5
        assert config.text_length == (3, 8)

    def test_from_json_file(self, sample_config_json):
        """Test loading config from JSON file."""
        config = GeneratorConfig.from_file(sample_config_json)

        assert config.seed == 456
        assert config.spacing == 3

    def test_to_yaml_file(self, temp_dir):
        """Test saving config to YAML file."""
        config = GeneratorConfig(seed=999, spacing=7)

        output_path = temp_dir / "output_config.yaml"
        config.to_file(output_path)

        assert output_path.exists()

        # Load it back
        loaded = GeneratorConfig.from_file(output_path)
        assert loaded.seed == 999
        assert loaded.spacing == 7

    def test_to_json_file(self, temp_dir):
        """Test saving config to JSON file."""
        config = GeneratorConfig(seed=888, spacing=4)

        output_path = temp_dir / "output_config.json"
        config.to_file(output_path)

        assert output_path.exists()

        # Verify JSON content
        with open(output_path) as f:
            data = json.load(f)
        assert data["seed"] == 888
        assert data["spacing"] == 4

    def test_ui_parameters_in_saved_config(self, temp_dir):
        """Test that new UI parameters are saved and loaded correctly."""
        config = GeneratorConfig(
            canvas_height=150,
            max_v_offset=25,
            font_scale=1.8,
        )

        output_path = temp_dir / "ui_params_config.yaml"
        config.to_file(output_path)

        # Load it back
        loaded = GeneratorConfig.from_file(output_path)
        assert loaded.canvas_height == 150
        assert loaded.max_v_offset == 25
        assert loaded.font_scale == 1.8


class TestCharacterConfig:
    """Tests for CharacterConfig."""

    def test_default_values(self):
        """Test default character configuration."""
        config = CharacterConfig()

        assert config.width == 64
        assert config.height == 64
        assert config.thickness == 2
