# 🍞 TextBaker

[![CI](https://github.com/q-viper/text-baker/actions/workflows/ci.yml/badge.svg)](https://github.com/q-viper/text-baker/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/q-viper/text-baker/badge.svg?branch=main)](https://coveralls.io/github/q-viper/text-baker?branch=main)
[![PyPI version](https://img.shields.io/pypi/v/textbaker.svg)](https://pypi.org/project/textbaker/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/textbaker.svg)](https://pypi.org/project/textbaker/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://q-viper.github.io/text-baker/)

> ⚠️ **Disclaimer**: This project was developed with the assistance of AI tools (GitHub Copilot). While efforts have been made to ensure quality, it may still contain errors or bugs. Use at your own discretion and feel free to report any issues.

**Synthetic Text Dataset Generator for OCR Training**

TextBaker is a powerful tool for generating synthetic text images by combining character datasets with backgrounds and applying various transformations. Perfect for training OCR models, data augmentation, and creating synthetic datasets.

![TextBaker Demo](assets/icon.png)

## ✨ Features

- 🎨 **GUI Application** - Interactive interface for real-time text generation
- 🖥️ **CLI Tool** - Batch processing from command line
- 📚 **Python Library** - Programmatic API for integration
- 🔄 **Transformations** - Rotation, perspective, scale, shear
- 🎭 **Textures** - Apply texture overlays to text
- 🖼️ **Backgrounds** - Composite text on background images
- 🎲 **Random Generation** - Generate random text with configurable parameters
- 🔧 **YAML/JSON Configs** - Save and load configurations
- 🎯 **Reproducible** - Seed-based random generation for reproducibility

## 📦 Installation

### From PyPI

```bash
pip install textbaker
```

### From Source

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

### GUI Application

Launch the interactive GUI:

```bash
textbaker
```

Or with pre-configured paths:

```bash
textbaker -d ./dataset -o ./output -b ./backgrounds -t ./textures
```

### Command Line

Generate text images from the command line:

```bash
# Generate specific texts
textbaker generate "Hello" "World" -d ./dataset -o ./output

# Generate 100 random samples
textbaker generate -n 100 --seed 42 -d ./dataset

# Apply transformations
textbaker generate "Hello" --rotation "-15,15" --perspective "0,0.1"

# With backgrounds and textures
textbaker generate "Hello" -b ./backgrounds -t ./textures --texture-opacity 0.8
```

### Python Library

```python
from textbaker import TextGenerator, GeneratorConfig, TransformConfig

# Simple usage
generator = TextGenerator()
result = generator.generate("Hello")
generator.save(result)

# With custom configuration
config = GeneratorConfig(
    seed=42,
    dataset={"dataset_dir": "./my_dataset"},
    transform=TransformConfig(
        rotation_range=(-15, 15),
        perspective_range=(0, 0.1),
        scale_range=(0.9, 1.1),
    ),
    output={"output_dir": "./output"},
)

generator = TextGenerator(config)

# Generate specific text
result = generator.generate("TextBaker")
print(f"Generated: {result.text}, Labels: {result.labels}")

# Generate random text
result = generator.generate_random(length=5)

# Batch generation
results = generator.batch_generate(["Hello", "World", "Test"])
```

## 📁 Dataset Structure

Organize your character images in folders named by the character:

```
dataset/
├── A/
│   ├── sample1.png
│   ├── sample2.png
│   └── ...
├── B/
│   └── ...
├── 0/
│   └── ...
└── special_char/
    └── ...
```

Each character folder should contain PNG images (preferably with transparency) of that character in various styles.

## ⚙️ Configuration

### YAML Configuration

Create a config file:

```bash
textbaker init-config -o config.yaml
```

Example `config.yaml`:

```yaml
seed: 42
dataset:
  dataset_dir: ./dataset
  recursive: true
  extensions: [".png", ".jpg"]
transform:
  rotation_range: [-15, 15]
  perspective_range: [0, 0.1]
  scale_range: [0.9, 1.1]
  shear_range: [0, 0]
color:
  random_color: true
  color_range_r: [0, 255]
  color_range_g: [0, 255]
  color_range_b: [0, 255]
texture:
  enabled: true
  texture_dir: ./textures
  opacity: 0.8
background:
  enabled: true
  background_dir: ./backgrounds
output:
  output_dir: ./output
  format: png
```

Use with CLI:

```bash
textbaker generate "Hello" --config config.yaml
```

Or in Python:

```python
from textbaker import GeneratorConfig, TextGenerator

config = GeneratorConfig.from_file("config.yaml")
generator = TextGenerator(config)
```

## 🎨 GUI Features

- **Character Selection** - Select which characters to use
- **Real-time Preview** - See generated text instantly
- **Drag & Drop** - Position text on canvas
- **Resize & Rotate** - Interactive handles for transformation
- **Texture Picker** - Select texture regions interactively
- **Background Selection** - Choose random backgrounds
- **Export** - Save generated images and configurations

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Mouse Wheel | Zoom in/out |
| Space + Drag | Pan view |
| Click + Drag | Move text |
| Corner handles | Resize text |
| Center handle | Rotate text |

## 🔧 CLI Commands

```bash
# Show help
textbaker --help

# Launch GUI
textbaker gui

# Generate images
textbaker generate --help

# Create config file
textbaker init-config --help
```

### Generate Command Options

| Option | Description |
|--------|-------------|
| `-d, --dataset` | Path to character dataset |
| `-o, --output` | Output directory |
| `-b, --background` | Background images directory |
| `-t, --texture` | Texture images directory |
| `-n, --count` | Number of random samples |
| `--seed` | Random seed for reproducibility |
| `-r, --rotation` | Rotation range (e.g., "-15,15") |
| `-p, --perspective` | Perspective range (e.g., "0,0.1") |
| `--scale` | Scale range (e.g., "0.9,1.1") |
| `--random-color` | Enable random coloring |
| `--color` | Fixed color (e.g., "255,0,0") |
| `--config` | Load from config file |

## 📖 API Reference

### TextGenerator

```python
class TextGenerator:
    def __init__(self, config: GeneratorConfig = None): ...
    def generate(self, text: str) -> GenerationResult: ...
    def generate_random(self, length: int = None) -> GenerationResult: ...
    def batch_generate(self, texts: list[str]) -> list[GenerationResult]: ...
    def save(self, result: GenerationResult, filename: str = None) -> Path: ...
    @property
    def available_characters(self) -> list[str]: ...
```

### GenerationResult

```python
@dataclass
class GenerationResult:
    image: np.ndarray  # BGRA image array
    text: str          # Generated text
    labels: list[str]  # Character labels
    seed: int          # Seed used
    params: dict       # Generation parameters
```

### Configuration Classes

- `GeneratorConfig` - Main configuration
- `TransformConfig` - Transformation settings
- `ColorConfig` - Color settings
- `TextureConfig` - Texture settings
- `BackgroundConfig` - Background settings
- `DatasetConfig` - Dataset settings
- `OutputConfig` - Output settings

## 🧪 Development

### Setup

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Run Linting

```bash
ruff check .
ruff format .
```

### Build Documentation

```bash
mkdocs serve
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👤 Author

**Ramkrishna Acharya** ([@q-viper](https://github.com/q-viper))

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython-6/)
- Image processing with [OpenCV](https://opencv.org/)
- CLI powered by [Typer](https://typer.tiangolo.com/)
