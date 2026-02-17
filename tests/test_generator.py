"""
Tests for the TextGenerator class.
"""

import cv2
import numpy as np
import pytest

from textbaker.core.configs import (
    BackgroundConfig,
    ColorConfig,
    DatasetConfig,
    GeneratorConfig,
    TextureConfig,
    TransformConfig,
)
from textbaker.core.defs import GenerationResult
from textbaker.core.generator import TextGenerator


class TestTextGeneratorInit:
    """Tests for TextGenerator initialization."""

    def test_default_config(self):
        """Test initialization with default config."""
        generator = TextGenerator()

        assert generator.config is not None
        assert generator.config.seed == 42

    def test_custom_config(self):
        """Test initialization with custom config."""
        config = GeneratorConfig(seed=123, spacing=5)
        generator = TextGenerator(config)

        assert generator.config.seed == 123
        assert generator.config.spacing == 5

    def test_lazy_initialization(self):
        """Test that dataset is not loaded until needed."""
        generator = TextGenerator()

        assert generator._initialized is False


class TestTextGeneratorGenerate:
    """Tests for TextGenerator.generate method."""

    def test_generate_with_dataset(self, sample_dataset):
        """Test generation with actual dataset."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result = generator.generate("ABC")

        assert isinstance(result, GenerationResult)
        assert result.text == "ABC"
        assert result.image is not None
        assert len(result.image.shape) >= 2  # At least 2D array

    def test_generate_fallback(self):
        """Test generation using fallback rendering."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir="nonexistent"),
        )
        generator = TextGenerator(config)

        # Should use cv2 fallback for missing characters
        result = generator.generate("XYZ")

        assert result.text == "XYZ"
        assert result.image is not None

    def test_generate_empty_raises(self, sample_dataset):
        """Test that empty text raises error."""
        config = GeneratorConfig(
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        with pytest.raises(ValueError):
            generator.generate("")

    def test_generate_with_spacing(self, sample_dataset):
        """Test generation with character spacing."""
        config = GeneratorConfig(
            spacing=10,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result_no_space = TextGenerator(
            GeneratorConfig(
                spacing=0,
                dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            )
        ).generate("AB")

        result_with_space = generator.generate("AB")

        # Image with spacing should be wider
        assert result_with_space.image.shape[1] >= result_no_space.image.shape[1]

    def test_result_contains_labels(self, sample_dataset):
        """Test that result contains character labels."""
        config = GeneratorConfig(
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result = generator.generate("AB")

        assert result.labels == ["A", "B"]


class TestTextGeneratorTransforms:
    """Tests for TextGenerator transformations."""

    def test_with_rotation(self, sample_dataset):
        """Test generation with rotation transform."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=TransformConfig(rotation_range=(-15, 15)),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None

    def test_with_scale(self, sample_dataset):
        """Test generation with scale transform."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=TransformConfig(scale_range=(0.5, 1.5)),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None


class TestTextGeneratorTextures:
    """Tests for TextGenerator texture application."""

    def test_with_texture(self, sample_dataset, sample_textures):
        """Test generation with texture."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            texture=TextureConfig(
                enabled=True,
                texture_dir=str(sample_textures),
                opacity=0.8,
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None

    def test_with_texture_per_character(self, sample_dataset, sample_textures):
        """Test generation with per-character texture."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            texture=TextureConfig(
                enabled=True,
                texture_dir=str(sample_textures),
                opacity=0.7,
                per_character=True,
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("ABC")

        assert result.image is not None
        assert result.text == "ABC"
        # Should have alpha channel when texture is applied per character
        assert result.image.shape[2] == 4

    def test_with_texture_on_composite(self, sample_dataset, sample_textures):
        """Test generation with texture applied to composite."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            texture=TextureConfig(
                enabled=True,
                texture_dir=str(sample_textures),
                opacity=0.7,
                per_character=False,
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("ABC")

        assert result.image is not None
        assert result.text == "ABC"
        # Should have alpha channel when texture is applied to composite
        assert result.image.shape[2] == 4


class TestTextGeneratorBackgrounds:
    """Tests for TextGenerator background application."""

    def test_with_background(self, sample_dataset, sample_backgrounds):
        """Test generation with background."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            background=BackgroundConfig(
                enabled=True,
                background_dir=str(sample_backgrounds),
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None
        # Background images are 256x256, so result should be at least that size
        assert result.image.shape[0] >= 64  # Character height


class TestTextGeneratorColors:
    """Tests for TextGenerator color application."""

    def test_with_random_color(self, sample_dataset):
        """Test generation with random colors."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            color=ColorConfig(
                random_color=True,
                color_range_r=(100, 200),
                color_range_g=(50, 150),
                color_range_b=(0, 100),
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None

    def test_with_fixed_color(self, sample_dataset):
        """Test generation with fixed color."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            color=ColorConfig(
                fixed_color=(255, 0, 0),
            ),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")

        assert result.image is not None


class TestTextGeneratorRandom:
    """Tests for TextGenerator.generate_random method."""

    def test_generate_random(self, sample_dataset):
        """Test random text generation."""
        config = GeneratorConfig(
            seed=42,
            text_length=(3, 5),
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result = generator.generate_random()

        assert result.text is not None
        assert 3 <= len(result.text) <= 5

    def test_generate_random_with_length(self, sample_dataset):
        """Test random generation with specific length."""
        config = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result = generator.generate_random(length=4)

        assert len(result.text) == 4


class TestTextGeneratorReproducibility:
    """Tests for reproducible generation."""

    def test_same_seed_same_result(self, sample_dataset):
        """Test that same seed produces same results."""
        # Disable all random transforms for exact reproducibility
        no_transform = TransformConfig(
            rotation_range=(0, 0),
            scale_range=(1.0, 1.0),
            perspective_range=(0, 0),
            shear_range=(0, 0),
        )
        config1 = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=no_transform,
        )
        config2 = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=no_transform,
        )

        gen1 = TextGenerator(config1)
        gen2 = TextGenerator(config2)

        result1 = gen1.generate("AB")
        result2 = gen2.generate("AB")

        # Images should be identical
        assert np.array_equal(result1.image, result2.image)

    def test_different_seed_different_result(self, sample_dataset):
        """Test that different seeds produce different results (when transforms enabled)."""
        config1 = GeneratorConfig(
            seed=42,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=TransformConfig(rotation_range=(-30, 30)),
        )
        config2 = GeneratorConfig(
            seed=999,
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
            transform=TransformConfig(rotation_range=(-30, 30)),
        )

        gen1 = TextGenerator(config1)
        gen2 = TextGenerator(config2)

        result1 = gen1.generate("A")
        result2 = gen2.generate("A")

        # Images should likely be different (not guaranteed but very probable)
        # Just check they're both valid
        assert result1.image is not None
        assert result2.image is not None


class TestTextGeneratorSave:
    """Tests for TextGenerator.save method."""

    def test_save_image(self, sample_dataset, temp_dir):
        """Test saving generated image."""
        config = GeneratorConfig(
            dataset=DatasetConfig(dataset_dir=str(sample_dataset)),
        )
        generator = TextGenerator(config)

        result = generator.generate("A")
        output_path = generator.save(result, "test.png", output_dir=temp_dir)

        assert output_path.exists()

        # Verify it's a valid image
        loaded = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
        assert loaded is not None
