"""
Basic Text Image Generation Example

This example demonstrates how to use the TextBaker library to generate
text images programmatically with textures and backgrounds.

Requirements:
    - textbaker package installed (pip install -e .)
    - Dataset in assets/dataset/ (character images organized by label)
    - Textures in assets/textures/
    - Backgrounds in assets/backgrounds/
"""

from pathlib import Path

import cv2

# Import TextBaker components
from textbaker import TextGenerator
from textbaker.core.configs import (
    BackgroundConfig,
    ColorConfig,
    DatasetConfig,
    GeneratorConfig,
    TextureConfig,
    TransformConfig,
)

# Get paths relative to this script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUT_DIR = SCRIPT_DIR / "output"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)


def example_basic_generation():
    """Basic text generation with default settings."""
    print("\n=== Example 1: Basic Generation ===")

    config = GeneratorConfig(
        seed=42,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("Hello")

    output_path = OUTPUT_DIR / "01_basic.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")
    print(f"Text: {result.text}, Size: {result.image.shape[:2]}")


def example_with_texture():
    """Generate text with texture overlay."""
    print("\n=== Example 2: With Texture ===")

    config = GeneratorConfig(
        seed=123,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.7,
            per_character=False,  # Same texture for all characters
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("Texture")

    output_path = OUTPUT_DIR / "02_with_texture.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def example_with_background():
    """Generate text on a background image."""
    print("\n=== Example 3: With Background ===")

    config = GeneratorConfig(
        seed=456,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
            mode="random",  # Random position on background
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("Background")

    output_path = OUTPUT_DIR / "03_with_background.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def example_with_texture_and_background():
    """Generate text with both texture and background."""
    print("\n=== Example 4: Texture + Background ===")

    config = GeneratorConfig(
        seed=789,
        spacing=5,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.8,
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
            mode="random",
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("TextBaker")

    output_path = OUTPUT_DIR / "04_texture_and_background.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def example_with_transforms():
    """Generate text with various transformations."""
    print("\n=== Example 5: With Transforms ===")

    config = GeneratorConfig(
        seed=101,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        transform=TransformConfig(
            rotation_range=(-15, 15),  # Random rotation between -15 and 15 degrees
            perspective_range=(0.0, 0.1),  # Slight perspective distortion
            scale_range=(0.8, 1.2),  # Scale variation
            shear_range=(-5, 5),  # Shear angle
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.6,
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("Transform")

    output_path = OUTPUT_DIR / "05_with_transforms.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def example_with_random_colors():
    """Generate text with random colors."""
    print("\n=== Example 6: Random Colors ===")

    config = GeneratorConfig(
        seed=202,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        color=ColorConfig(
            random_color=True,
            color_range_r=(100, 255),  # Red range
            color_range_g=(50, 200),  # Green range
            color_range_b=(50, 200),  # Blue range
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
        ),
    )

    generator = TextGenerator(config)
    result = generator.generate("Colors")

    output_path = OUTPUT_DIR / "06_random_colors.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def example_batch_generation():
    """Generate multiple text images in a batch."""
    print("\n=== Example 7: Batch Generation ===")

    config = GeneratorConfig(
        seed=303,
        text_length=(4, 8),  # Random length between 4 and 8 characters
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.7,
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
        ),
        transform=TransformConfig(
            rotation_range=(-10, 10),
            scale_range=(0.9, 1.1),
        ),
    )

    generator = TextGenerator(config)

    # Generate 5 random text images
    for i in range(5):
        result = generator.generate_random()
        output_path = OUTPUT_DIR / f"07_batch_{i:02d}_{result.text}.png"
        cv2.imwrite(str(output_path), result.image)
        print(f"Generated: {output_path} - Text: '{result.text}'")


def example_full_pipeline():
    """Complete pipeline with all features enabled."""
    print("\n=== Example 8: Full Pipeline ===")

    config = GeneratorConfig(
        seed=42,
        spacing=3,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
            recursive=True,
        ),
        transform=TransformConfig(
            rotation_range=(-12, 12),
            perspective_range=(0.0, 0.08),
            scale_range=(0.85, 1.15),
            shear_range=(-3, 3),
        ),
        color=ColorConfig(
            random_color=True,
            color_range_r=(80, 255),
            color_range_g=(80, 255),
            color_range_b=(80, 255),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.75,
            per_character=True,  # Different texture per character
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
            mode="random",
        ),
    )

    generator = TextGenerator(config)

    # Generate specific texts
    texts = ["Hello", "World", "TextBaker", "Python", "OpenCV"]

    for text in texts:
        result = generator.generate(text)
        output_path = OUTPUT_DIR / f"08_full_{text.lower()}.png"
        cv2.imwrite(str(output_path), result.image)
        print(f"Generated: {output_path}")


def example_from_config_file():
    """Load configuration from a YAML file."""
    print("\n=== Example 9: From Config File ===")

    # First, create a sample config file
    config = GeneratorConfig(
        seed=999,
        spacing=2,
        dataset=DatasetConfig(
            dataset_dir=str(ASSETS_DIR / "dataset"),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(ASSETS_DIR / "textures"),
            opacity=0.8,
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(ASSETS_DIR / "backgrounds"),
        ),
    )

    # Save config to file
    config_path = OUTPUT_DIR / "sample_config.yaml"
    config.to_file(config_path)
    print(f"Saved config to: {config_path}")

    # Load config from file and generate
    loaded_config = GeneratorConfig.from_file(config_path)
    generator = TextGenerator(loaded_config)
    result = generator.generate("FromConfig")

    output_path = OUTPUT_DIR / "09_from_config.png"
    cv2.imwrite(str(output_path), result.image)
    print(f"Generated: {output_path}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("TextBaker - Python Module Examples")
    print("=" * 60)

    # Run all examples
    example_basic_generation()
    example_with_texture()
    example_with_background()
    example_with_texture_and_background()
    example_with_transforms()
    example_with_random_colors()
    example_batch_generation()
    example_full_pipeline()
    example_from_config_file()

    print("\n" + "=" * 60)
    print(f"All examples completed! Output saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
