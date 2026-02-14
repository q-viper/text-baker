# TextBaker

**Synthetic Text Dataset Generator for OCR Training**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/q-viper/text-baker/blob/main/LICENSE)

---

## Installation

```bash
pip install textbaker
```

**From source:**

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e .
```

---

## Quick Start

### GUI Application

```bash
# Launch GUI (default seed: 42)
textbaker gui

# With custom seed for reproducibility
textbaker gui --seed 123

# With custom paths
textbaker gui -d ./my_dataset -o ./output -b ./backgrounds
```

### Command Line Generation

```bash
# Generate specific texts
textbaker generate "hello" "world" "test123"

# Generate 100 random samples
textbaker generate -n 100 --seed 42

# Create default config file
textbaker init-config -o my_config.json
```

### Python Library

```python
from textbaker import TextGenerator, GeneratorConfig, TransformConfig

# Simple usage
generator = TextGenerator()
result = generator.generate("hello")
generator.save(result)

# With custom configuration
config = GeneratorConfig(
    seed=42,
    spacing=5,
    transform=TransformConfig(
        rotation_range=(-15, 15),
        scale_range=(0.9, 1.1),
    ),
)
generator = TextGenerator(config)

# Generate random text
result = generator.generate_random(length=5)

# Batch generation
results = generator.batch_generate(["hello", "world", "test"])
```

---

## Default Folder Structure

```
project/
├── assets/
│   ├── dataset/      # Character images by folder
│   ├── backgrounds/  # Background images
│   └── textures/     # Texture images
└── output/           # Generated images
```

---

## CLI Commands

### `textbaker gui`

Launch the GUI application.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--dataset` | `-d` | `assets/dataset` | Character dataset folder |
| `--output` | `-o` | `output` | Output folder |
| `--backgrounds` | `-b` | `assets/backgrounds` | Background images |
| `--textures` | `-t` | `assets/textures` | Texture images |
| `--seed` | `-s` | `42` | Random seed |
| `--config` | `-c` | | Config file (JSON/YAML) |

### `textbaker generate`

Generate images from command line (no GUI).

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--config` | `-c` | | Config file |
| `--dataset` | `-d` | `assets/dataset` | Dataset folder |
| `--output` | `-o` | `output` | Output folder |
| `--seed` | `-s` | `42` | Random seed |
| `--count` | `-n` | `10` | Number of random samples |
| `--length` | `-l` | random | Text length |
| `--spacing` | | `0` | Spacing between chars |

### `textbaker init-config`

Create a default configuration file.

---

## Configuration

Create a config file with all options:

```bash
textbaker init-config -o config.json
```

Example config:

```json
{
  "seed": 42,
  "spacing": 5,
  "text_length": [1, 10],
  "dataset": {
    "dataset_dir": "assets/dataset",
    "recursive": true
  },
  "transform": {
    "rotation_range": [-15, 15],
    "scale_range": [0.9, 1.1]
  },
  "color": {
    "random_color": false
  },
  "output": {
    "output_dir": "output",
    "format": "png"
  }
}
```

---

## Python API Reference

### TextGenerator

Main class for programmatic text generation.

```python
from textbaker import TextGenerator, GeneratorConfig

# Initialize
generator = TextGenerator(config=None)  # Uses defaults

# Properties
generator.available_characters  # List of character labels

# Methods
generator.generate(text: str) -> GenerationResult
generator.generate_random(length: int = None) -> GenerationResult
generator.save(result, filename=None, output_dir=None) -> Path
generator.batch_generate(texts: List[str]) -> List[GenerationResult]
generator.reset_seed(seed: int = None)
```

### GeneratorConfig

Pydantic configuration model.

```python
from textbaker import (
    GeneratorConfig,
    TransformConfig,
    ColorConfig,
    TextureConfig,
    BackgroundConfig,
    OutputConfig,
    DatasetConfig,
)

config = GeneratorConfig(
    seed=42,
    spacing=0,
    text_length=(1, 10),
    dataset=DatasetConfig(...),
    transform=TransformConfig(...),
    color=ColorConfig(...),
    texture=TextureConfig(...),
    background=BackgroundConfig(...),
    output=OutputConfig(...),
)

# Load/save config
config = GeneratorConfig.from_file("config.json")
config.to_file("config.yaml")
```

### Global Random State

```python
from textbaker import rng

rng.seed(42)              # Set seed
rng.current_seed          # Get current seed
rng.randint(0, 100)       # Random integer
rng.uniform(0.0, 1.0)     # Random float
rng.choice(items)         # Random choice
rng.choices(items, k=5)   # Multiple choices
rng.shuffle(items)        # Shuffle in place
```

---

## Dataset Structure

Images are scanned **recursively**. Parent folder name = character label:

```
assets/dataset/
├── A/
│   └── sample1.png  → label "A"
├── B/
│   └── sample1.png  → label "B"
└── digits/
    └── 0/
        └── sample1.png  → label "0"
```

---

## GUI Shortcuts

| Shortcut | Action |
|----------|--------|
| Scroll | Zoom |
| Space + Drag | Pan |
| Drag text | Move |
| Blue circle | Rotate |
| Corners | Resize |

---

## Author

**Ramkrishna Acharya** — [GitHub](https://github.com/q-viper)

## License

MIT License — see [LICENSE](https://github.com/q-viper/text-baker/blob/main/LICENSE)
