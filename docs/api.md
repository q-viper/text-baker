# API Reference

Complete API documentation for TextBaker.

---

## TextGenerator

Main class for programmatic text generation.

::: textbaker.core.generator.TextGenerator
    options:
      show_source: false
      members:
        - __init__
        - generate
        - generate_random
        - save
        - batch_generate
        - reset_seed
        - available_characters

---

## Configuration Classes

### GeneratorConfig

Main configuration class for text generation.

::: textbaker.core.configs.GeneratorConfig
    options:
      show_source: false

### TransformConfig

Configuration for image transformations.

::: textbaker.core.configs.TransformConfig
    options:
      show_source: false

### ColorConfig

Configuration for color manipulation.

::: textbaker.core.configs.ColorConfig
    options:
      show_source: false

### TextureConfig

Configuration for texture application.

::: textbaker.core.configs.TextureConfig
    options:
      show_source: false

### BackgroundConfig

Configuration for background handling.

::: textbaker.core.configs.BackgroundConfig
    options:
      show_source: false

### DatasetConfig

Configuration for dataset loading.

::: textbaker.core.configs.DatasetConfig
    options:
      show_source: false

### OutputConfig

Configuration for output settings.

::: textbaker.core.configs.OutputConfig
    options:
      show_source: false

---

## Data Classes

### GenerationResult

Result of a text generation operation.

::: textbaker.core.defs.GenerationResult
    options:
      show_source: false

### GeneratedText

Generated text with metadata.

::: textbaker.core.defs.GeneratedText
    options:
      show_source: false

---

## Random State

Global random state for reproducibility.

```python
from textbaker import rng

# Set seed for reproducibility
rng.seed(42)

# Get current seed
print(rng.current_seed)

# Random operations
rng.randint(0, 100)       # Random integer in range
rng.uniform(0.0, 1.0)     # Random float in range
rng.choice(items)         # Random choice from list
rng.choices(items, k=5)   # Multiple random choices
rng.shuffle(items)        # Shuffle list in place
```

---

## CLI Commands

### `textbaker gui`

Launch the graphical user interface.

```bash
textbaker gui [OPTIONS]
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--dataset` | `-d` | `assets/dataset` | Character dataset folder |
| `--output` | `-o` | `output` | Output folder |
| `--backgrounds` | `-b` | `assets/backgrounds` | Background images folder |
| `--textures` | `-t` | `assets/textures` | Texture images folder |
| `--seed` | `-s` | `42` | Random seed |
| `--config` | `-c` | | Config file path |

### `textbaker generate`

Generate images from the command line.

```bash
textbaker generate [TEXTS]... [OPTIONS]
```

**Arguments:**

- `TEXTS`: Text strings to generate (optional, uses random if not provided)

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |
| `--dataset` | `-d` | Dataset folder |
| `--output` | `-o` | Output folder |
| `--seed` | `-s` | Random seed |
| `--count` | `-n` | Number of random samples |
| `--length` | `-l` | Text length for random generation |
| `--spacing` | | Spacing between characters |
| `--rotation` | `-r` | Rotation range (e.g., "-15,15") |
| `--perspective` | `-p` | Perspective range (e.g., "0,0.1") |
| `--scale` | | Scale range (e.g., "0.8,1.2") |
| `--shear` | | Shear range (e.g., "-10,10") |
| `--backgrounds` | `-b` | Background images folder |
| `--bg-color` | | Solid color (e.g., "255,255,255") |
| `--textures` | `-t` | Texture images folder |
| `--texture-opacity` | | Texture opacity (0.0-1.0) |
| `--random-color` | | Apply random colors |
| `--color` | | Fixed color (e.g., "0,0,255") |

### `textbaker init-config`

Create a default configuration file.

```bash
textbaker init-config [OPTIONS]
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `textbaker_config.yaml` | Output file path |
| `--format` | `-f` | `yaml` | Format (json or yaml) |
