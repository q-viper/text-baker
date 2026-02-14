# Configuration Reference

TextBaker uses a hierarchical configuration system with Pydantic models. Configurations can be saved and loaded from YAML or JSON files.

---

## Quick Start

Create a default config file:

```bash
textbaker init-config -o config.yaml
```

Use a config file:

```bash
# CLI
textbaker generate "Hello" --config config.yaml

# Python
from textbaker import GeneratorConfig, TextGenerator
config = GeneratorConfig.from_file("config.yaml")
generator = TextGenerator(config)
```

---

## Configuration Structure

```yaml
# Main settings
seed: 42
spacing: 0
text_length: [1, 10]

# Sub-configurations
dataset:
  dataset_dir: assets/dataset
  recursive: true
  extensions: [".png", ".jpg", ".jpeg"]

transform:
  rotation_range: [-15, 15]
  perspective_range: [0, 0.1]
  scale_range: [0.9, 1.1]
  shear_range: [0, 0]

color:
  random_color: false
  fixed_color: null
  color_range_r: [0, 255]
  color_range_g: [0, 255]
  color_range_b: [0, 255]

texture:
  enabled: false
  texture_dir: assets/textures
  opacity: 0.8
  per_character: false

background:
  enabled: false
  background_dir: assets/backgrounds
  mode: random

character:
  font: FONT_HERSHEY_SIMPLEX
  font_scale: 1.0
  thickness: 1

output:
  output_dir: output
  format: png
  quality: 95
```

---

## GeneratorConfig

Main configuration class.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `seed` | `int` | `42` | Random seed for reproducibility |
| `spacing` | `int` | `0` | Pixel spacing between characters |
| `text_length` | `tuple[int, int]` | `(1, 10)` | Random text length range |
| `dataset` | `DatasetConfig` | | Dataset settings |
| `transform` | `TransformConfig` | | Transform settings |
| `color` | `ColorConfig` | | Color settings |
| `texture` | `TextureConfig` | | Texture settings |
| `background` | `BackgroundConfig` | | Background settings |
| `character` | `CharacterConfig` | | Character/font settings |
| `output` | `OutputConfig` | | Output settings |

---

## DatasetConfig

Character dataset settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dataset_dir` | `str` | `"assets/dataset"` | Path to character images |
| `recursive` | `bool` | `True` | Scan subdirectories |
| `extensions` | `list[str]` | `[".png", ".jpg", ".jpeg"]` | Image extensions |

---

## TransformConfig

Image transformation settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rotation_range` | `tuple[float, float]` | `(0, 0)` | Rotation angle range in degrees |
| `perspective_range` | `tuple[float, float]` | `(0, 0)` | Perspective distortion range |
| `scale_range` | `tuple[float, float]` | `(1.0, 1.0)` | Scale factor range |
| `shear_range` | `tuple[float, float]` | `(0, 0)` | Shear angle range in degrees |

**Example:**

```python
transform=TransformConfig(
    rotation_range=(-15, 15),      # Rotate ±15 degrees
    perspective_range=(0, 0.1),    # 0-10% perspective
    scale_range=(0.8, 1.2),        # 80-120% scale
    shear_range=(-5, 5),           # Shear ±5 degrees
)
```

---

## ColorConfig

Text coloring settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `random_color` | `bool` | `False` | Enable random colors per character |
| `fixed_color` | `tuple[int, int, int]` | `None` | Fixed BGR color |
| `color_range_r` | `tuple[int, int]` | `(0, 255)` | Red channel range |
| `color_range_g` | `tuple[int, int]` | `(0, 255)` | Green channel range |
| `color_range_b` | `tuple[int, int]` | `(0, 255)` | Blue channel range |

**Example:**

```python
# Random colors in specific ranges
color=ColorConfig(
    random_color=True,
    color_range_r=(100, 255),  # Bright reds
    color_range_g=(0, 100),    # Dark greens
    color_range_b=(0, 100),    # Dark blues
)

# Fixed white color
color=ColorConfig(
    random_color=False,
    fixed_color=(255, 255, 255),
)
```

---

## TextureConfig

Texture overlay settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable texture overlay |
| `texture_dir` | `str` | `"assets/textures"` | Path to texture images |
| `opacity` | `float` | `0.8` | Texture opacity (0.0-1.0) |
| `per_character` | `bool` | `False` | Different texture per character |

**Example:**

```python
texture=TextureConfig(
    enabled=True,
    texture_dir="assets/textures",
    opacity=0.7,
    per_character=True,
)
```

---

## BackgroundConfig

Background composition settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable background |
| `background_dir` | `str` | `"assets/backgrounds"` | Path to background images |
| `mode` | `str` | `"random"` | Placement mode |

**Example:**

```python
background=BackgroundConfig(
    enabled=True,
    background_dir="assets/backgrounds",
    mode="random",
)
```

---

## CharacterConfig

Font and character rendering settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `font` | `str` | `"FONT_HERSHEY_SIMPLEX"` | OpenCV font name |
| `font_scale` | `float` | `1.0` | Font scale factor |
| `thickness` | `int` | `1` | Line thickness |

**Available fonts:**

- `FONT_HERSHEY_SIMPLEX` - Normal size sans-serif
- `FONT_HERSHEY_PLAIN` - Small size sans-serif
- `FONT_HERSHEY_DUPLEX` - Normal size sans-serif (more complex)
- `FONT_HERSHEY_COMPLEX` - Normal size serif
- `FONT_HERSHEY_TRIPLEX` - Normal size serif (more complex)
- `FONT_HERSHEY_SCRIPT_SIMPLEX` - Hand-writing style
- `FONT_HERSHEY_SCRIPT_COMPLEX` - Hand-writing style (more complex)

**Example:**

```python
character=CharacterConfig(
    font="FONT_HERSHEY_SCRIPT_COMPLEX",
    font_scale=2.5,
    thickness=2,
)
```

---

## OutputConfig

Output settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `output_dir` | `str` | `"output"` | Output directory |
| `format` | `str` | `"png"` | Image format (png, jpg) |
| `quality` | `int` | `95` | JPEG quality (1-100) |

---

## Loading and Saving

```python
from textbaker import GeneratorConfig

# From file
config = GeneratorConfig.from_file("config.yaml")
config = GeneratorConfig.from_file("config.json")

# Save to file
config.to_file("config.yaml")
config.to_file("config.json")

# From dictionary
config = GeneratorConfig(**config_dict)

# To dictionary
config_dict = config.model_dump()
```

---

## Full Example

```python
from textbaker import TextGenerator, GeneratorConfig
from textbaker.core.configs import (
    DatasetConfig,
    TransformConfig,
    ColorConfig,
    TextureConfig,
    BackgroundConfig,
    CharacterConfig,
    OutputConfig,
)

config = GeneratorConfig(
    seed=42,
    spacing=2,
    text_length=(4, 8),
    dataset=DatasetConfig(
        dataset_dir="assets/dataset",
        recursive=True,
    ),
    transform=TransformConfig(
        rotation_range=(-15, 15),
        perspective_range=(0, 0.08),
        scale_range=(0.9, 1.1),
    ),
    color=ColorConfig(
        random_color=True,
        color_range_r=(100, 255),
        color_range_g=(50, 200),
        color_range_b=(50, 200),
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
    character=CharacterConfig(
        font="FONT_HERSHEY_DUPLEX",
        font_scale=2.0,
        thickness=2,
    ),
    output=OutputConfig(
        output_dir="output",
        format="png",
    ),
)

# Save for later use
config.to_file("my_config.yaml")

# Use the config
generator = TextGenerator(config)
result = generator.generate("Hello")
```
