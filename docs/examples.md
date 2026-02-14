# Examples

This page demonstrates various ways to use TextBaker programmatically.

All examples can be found in the [`examples/`](https://github.com/q-viper/text-baker/tree/main/examples) folder.

---

## Basic Text Generation

Generate text images with default settings:

```python
from textbaker import TextGenerator
from textbaker.core.configs import GeneratorConfig, DatasetConfig

config = GeneratorConfig(
    seed=42,
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
    ),
)

generator = TextGenerator(config)
result = generator.generate("Hello")

# Save the result
import cv2
cv2.imwrite("hello.png", result.image)
print(f"Generated: {result.text}, Size: {result.image.shape[:2]}")
```

---

## With Texture Overlay

Apply textures to the generated text:

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    TextureConfig,
)

config = GeneratorConfig(
    seed=123,
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
    ),
    texture=TextureConfig(
        enabled=True,
        texture_dir="assets/textures",
        opacity=0.7,
        per_character=False,  # Same texture for all characters
    ),
)

generator = TextGenerator(config)
result = generator.generate("Texture")
cv2.imwrite("textured.png", result.image)
```

---

## With Background Image

Place generated text on background images:

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    BackgroundConfig,
)

config = GeneratorConfig(
    seed=456,
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
    ),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
        mode="random",  # Random position on background
    ),
)

generator = TextGenerator(config)
result = generator.generate("Background")
cv2.imwrite("with_background.png", result.image)
```

---

## Full Pipeline

Combine textures, backgrounds, transforms, and colors:

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    TransformConfig,
    ColorConfig,
    TextureConfig,
    BackgroundConfig,
)

config = GeneratorConfig(
    seed=42,
    spacing=3,
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
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
        texture_dir="assets/textures",
        opacity=0.75,
        per_character=True,
    ),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
        mode="random",
    ),
)

generator = TextGenerator(config)

# Generate multiple texts
texts = ["Hello", "World", "TextBaker", "Python"]
for text in texts:
    result = generator.generate(text)
    cv2.imwrite(f"{text.lower()}.png", result.image)
    print(f"Generated: {result.text}")
```

---

## Batch Generation

Generate many random samples for training:

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    TransformConfig,
    TextureConfig,
    BackgroundConfig,
)
from pathlib import Path

config = GeneratorConfig(
    seed=303,
    text_length=(4, 8),  # Random length between 4 and 8
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
    ),
    transform=TransformConfig(
        rotation_range=(-10, 10),
        scale_range=(0.9, 1.1),
    ),
    texture=TextureConfig(
        enabled=True,
        texture_dir="assets/textures",
        opacity=0.7,
    ),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
    ),
)

generator = TextGenerator(config)
output_dir = Path("batch_output")
output_dir.mkdir(exist_ok=True)

# Generate 100 random samples
for i in range(100):
    result = generator.generate_random()
    output_path = output_dir / f"{i:04d}_{result.text}.png"
    cv2.imwrite(str(output_path), result.image)

print(f"Generated 100 samples in {output_dir}")
```

---

## Using Config Files

Save and load configurations from YAML/JSON:

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    TextureConfig,
    BackgroundConfig,
)

# Create and save config
config = GeneratorConfig(
    seed=999,
    spacing=2,
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
    ),
    texture=TextureConfig(
        enabled=True,
        texture_dir="assets/textures",
        opacity=0.8,
    ),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
    ),
)

# Save to YAML
config.to_file("my_config.yaml")

# Later, load and use
loaded_config = GeneratorConfig.from_file("my_config.yaml")
generator = TextGenerator(loaded_config)
result = generator.generate("FromConfig")
```

---

## CLI Examples

Generate images from the command line:

```bash
# Basic generation
textbaker generate "hello" "world"

# With transforms
textbaker generate "test" --rotation "-15,15" --perspective "0.0,0.1"

# With background images
textbaker generate "test" -b ./assets/backgrounds

# With textures
textbaker generate "test" -t ./assets/textures --texture-opacity 0.8

# Random colors
textbaker generate "test" --random-color

# Full pipeline
textbaker generate "hello" \
    -r "-10,10" \
    -p "0,0.05" \
    -b ./assets/backgrounds \
    -t ./assets/textures \
    --random-color

# Generate 50 random samples
textbaker generate -n 50 --seed 42
```

---

## Running Examples

To run the included examples:

```bash
# Install textbaker
pip install -e .

# Run basic generation example
python examples/basic_generation.py

# Generate app icons
python examples/generate_icon.py
```

Output will be saved to `examples/output/`.
