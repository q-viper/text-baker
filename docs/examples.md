# Examples

This page demonstrates various ways to use TextBaker programmatically with visual outputs.

All examples can be found in the [`examples/`](https://github.com/q-viper/text-baker/tree/main/examples) folder.

---

## 1. Basic Text Generation

Generate text images with default settings using characters from your dataset.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import DatasetConfig, TransformConfig

config = GeneratorConfig(
    seed=42,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
    transform=TransformConfig(
        rotation_range=(0, 0),
        scale_range=(1.0, 1.0),
    ),
)

generator = TextGenerator(config)
result = generator.generate("12345")
cv2.imwrite("example_basic.png", result.image)
```

**Output:**

![Basic](assets/readme/example_basic.png)

---

## 2. With Transformations

Apply rotation, perspective, and scale transformations.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, TransformConfig, CharacterConfig
)

config = GeneratorConfig(
    seed=123,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
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
cv2.imwrite("example_rotated.png", result.image)
```

**Output:**

![Transformed](assets/readme/example_rotated.png)

---

## 3. Random Colors

Generate text with random colors per character.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, ColorConfig, CharacterConfig
)

config = GeneratorConfig(
    seed=456,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
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
result = generator.generate("Hello")
cv2.imwrite("example_colored.png", result.image)
```

**Output:**

![Colored](assets/readme/example_colored.png)

---

## 4. With Background Image

Place generated text on background images.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, BackgroundConfig, 
    ColorConfig, CharacterConfig
)

config = GeneratorConfig(
    seed=789,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
    ),
    color=ColorConfig(
        random_color=False,
        fixed_color=(255, 255, 255),  # White text
    ),
    character=CharacterConfig(
        font="FONT_HERSHEY_TRIPLEX",
        font_scale=3.0,
        thickness=2,
    ),
)

generator = TextGenerator(config)
result = generator.generate("World")
cv2.imwrite("example_background.png", result.image)
```

**Output:**

![Background](assets/readme/example_background.png)

---

## 5. With Texture Overlay

Apply textures to the generated text.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, TextureConfig, 
    TransformConfig, CharacterConfig
)

config = GeneratorConfig(
    seed=555,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
    texture=TextureConfig(
        enabled=True,
        texture_dir="assets/textures",
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
cv2.imwrite("example_texture.png", result.image)
```

**Output:**

![Texture](assets/readme/example_texture.png)

---

## 6. Full Pipeline

Combine transforms, colors, textures, and backgrounds.

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, TransformConfig, ColorConfig,
    TextureConfig, BackgroundConfig, CharacterConfig
)

config = GeneratorConfig(
    seed=999,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
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
        texture_dir="assets/textures",
        opacity=0.4,
    ),
    background=BackgroundConfig(
        enabled=True,
        background_dir="assets/backgrounds",
    ),
    character=CharacterConfig(
        font="FONT_HERSHEY_SCRIPT_SIMPLEX",
        font_scale=2.0,
        thickness=2,
    ),
)

generator = TextGenerator(config)
result = generator.generate("TextBaker")
cv2.imwrite("example_full.png", result.image)
```

**Output:**

![Full Pipeline](assets/readme/example_full.png)

---

## Batch Generation

Generate many random samples for training:

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, TransformConfig, 
    TextureConfig, BackgroundConfig
)
from pathlib import Path

config = GeneratorConfig(
    seed=303,
    text_length=(4, 8),  # Random length between 4 and 8
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
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
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig, TextureConfig, BackgroundConfig
)

# Create and save config
config = GeneratorConfig(
    seed=999,
    spacing=2,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
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

## Generate Example Images

To regenerate the example images shown above, run:

```bash
python examples/generate_readme_images.py
```

Output will be saved to `assets/readme/`.
