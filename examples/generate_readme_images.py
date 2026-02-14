#!/usr/bin/env python3
"""Generate example images for the README and documentation."""

import sys
from pathlib import Path

import cv2

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from textbaker import GeneratorConfig, TextGenerator
from textbaker.core.configs import (
    BackgroundConfig,
    CharacterConfig,
    ColorConfig,
    DatasetConfig,
    TextureConfig,
    TransformConfig,
)

ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = ASSETS_DIR / "readme"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use actual assets
DATASET_DIR = ASSETS_DIR / "dataset"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
TEXTURES_DIR = ASSETS_DIR / "textures"

# Available CV2 fonts for variety
CV2_FONTS = {
    "simplex": cv2.FONT_HERSHEY_SIMPLEX,
    "plain": cv2.FONT_HERSHEY_PLAIN,
    "duplex": cv2.FONT_HERSHEY_DUPLEX,
    "complex": cv2.FONT_HERSHEY_COMPLEX,
    "triplex": cv2.FONT_HERSHEY_TRIPLEX,
    "script_simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    "script_complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
}


def generate_examples():
    """Generate example images for README."""
    print("=" * 60)
    print("Generating README example images")
    print("=" * 60)
    print(f"Dataset: {DATASET_DIR}")
    print(f"Backgrounds: {BACKGROUNDS_DIR}")
    print(f"Textures: {TEXTURES_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Example 1: Basic text generation (numbers from dataset)
    print("1. Generating basic example (numbers)...")
    config = GeneratorConfig(
        seed=42,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        transform=TransformConfig(
            rotation_range=(0, 0),
            scale_range=(1.0, 1.0),
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("12345")
    cv2.imwrite(str(OUTPUT_DIR / "example_basic.png"), result.image)
    print("   ✓ Saved: example_basic.png")

    # Example 2: With rotation and perspective
    print("2. Generating transformed example...")
    config = GeneratorConfig(
        seed=123,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        transform=TransformConfig(
            rotation_range=(-20, 20),
            perspective_range=(0.0, 0.08),
            scale_range=(0.9, 1.1),
        ),
        character=CharacterConfig(
            font="FONT_HERSHEY_DUPLEX",
            font_scale=2.0,
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("67890")
    cv2.imwrite(str(OUTPUT_DIR / "example_rotated.png"), result.image)
    print("   ✓ Saved: example_rotated.png")

    # Example 3: With random colors (using script font for fallback chars)
    print("3. Generating colored example...")
    config = GeneratorConfig(
        seed=456,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        color=ColorConfig(
            random_color=True,
            color_range_r=(100, 255),
            color_range_g=(50, 200),
            color_range_b=(50, 255),
        ),
        character=CharacterConfig(
            font="FONT_HERSHEY_SCRIPT_COMPLEX",
            font_scale=2.5,
            thickness=2,
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("Hello")  # Uses fallback for letters
    cv2.imwrite(str(OUTPUT_DIR / "example_colored.png"), result.image)
    print("   ✓ Saved: example_colored.png")

    # Example 4: With background
    print("4. Generating with background...")
    config = GeneratorConfig(
        seed=789,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(BACKGROUNDS_DIR),
        ),
        color=ColorConfig(
            random_color=False,
            fixed_color=(255, 255, 255),  # White text on background
        ),
        character=CharacterConfig(
            font="FONT_HERSHEY_TRIPLEX",
            font_scale=3.0,
            thickness=2,
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("World")
    cv2.imwrite(str(OUTPUT_DIR / "example_background.png"), result.image)
    print("   ✓ Saved: example_background.png")

    # Example 5: With texture overlay
    print("5. Generating with texture...")
    config = GeneratorConfig(
        seed=555,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(TEXTURES_DIR),
            opacity=0.7,
        ),
        transform=TransformConfig(
            rotation_range=(-5, 5),
            scale_range=(1.0, 1.0),
        ),
        character=CharacterConfig(
            font="FONT_HERSHEY_COMPLEX",
            font_scale=2.5,
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("Baker")
    cv2.imwrite(str(OUTPUT_DIR / "example_texture.png"), result.image)
    print("   ✓ Saved: example_texture.png")

    # Example 6: Full pipeline - transforms + colors + texture + background
    print("6. Generating full pipeline example...")
    config = GeneratorConfig(
        seed=999,
        dataset=DatasetConfig(dataset_dir=str(DATASET_DIR)),
        transform=TransformConfig(
            rotation_range=(-15, 15),
            perspective_range=(0, 0.05),
            scale_range=(0.95, 1.05),
        ),
        color=ColorConfig(
            random_color=True,
            color_range_r=(150, 255),
            color_range_g=(100, 200),
            color_range_b=(50, 150),
        ),
        texture=TextureConfig(
            enabled=True,
            texture_dir=str(TEXTURES_DIR),
            opacity=0.4,
        ),
        background=BackgroundConfig(
            enabled=True,
            background_dir=str(BACKGROUNDS_DIR),
        ),
        character=CharacterConfig(
            font="FONT_HERSHEY_SCRIPT_SIMPLEX",
            font_scale=2.0,
            thickness=2,
        ),
    )
    generator = TextGenerator(config)
    result = generator.generate("TextBaker")
    cv2.imwrite(str(OUTPUT_DIR / "example_full.png"), result.image)
    print("   ✓ Saved: example_full.png")

    print()
    print("=" * 60)
    print("✅ All README examples generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    generate_examples()
