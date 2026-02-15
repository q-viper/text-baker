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

TextBaker generates synthetic text images by combining character datasets with backgrounds and applying transformations. Perfect for training OCR models and data augmentation.

<p align="center">
  <img src="https://raw.githubusercontent.com/q-viper/text-baker/main/assets/icon.png" alt="TextBaker Icon" width="128">
</p>

## 🖼️ Example Outputs

| Basic | Transformed | Colored | Background | Texture | Full Pipeline |
|:-----:|:-----------:|:-------:|:----------:|:-------:|:-------------:|
| ![Basic](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_basic.png) | ![Rotated](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_rotated.png) | ![Colored](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_colored.png) | ![Background](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_background.png) | ![Texture](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_texture.png) | ![Full](https://raw.githubusercontent.com/q-viper/text-baker/main/assets/readme/example_full.png) |

📖 See [Examples Documentation](https://q-viper.github.io/text-baker/examples/) for code samples.

## ✨ Features

- 🎨 **GUI Application** - Interactive interface for real-time text generation
- ✏️ **Custom Character Drawing** - Draw and save custom characters directly in the app
- 🖥️ **CLI Tool** - Batch processing from command line
- 📚 **Python Library** - Programmatic API for integration
- 🔄 **Transformations** - Rotation, perspective, scale, shear
- 🎭 **Textures & Backgrounds** - Apply overlays and composite on images
- 🔧 **YAML/JSON Configs** - Save and load configurations

## 📦 Installation

```bash
pip install textbaker
```

Or from source:

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e .
```

## 🚀 Quick Start

### GUI

```bash
textbaker
```

### CLI

```bash
# Generate specific texts
textbaker generate "Hello" "World" -d ./dataset -o ./output

# Generate random samples with transforms
textbaker generate -n 100 --seed 42 -r "-15,15" -b ./backgrounds
```

### Python

```python
from textbaker import TextGenerator, GeneratorConfig

generator = TextGenerator()
result = generator.generate("Hello")
generator.save(result)
```

📖 See [full documentation](https://q-viper.github.io/text-baker/) for detailed usage.

## 📁 Dataset Structure

```
dataset/
├── A/
│   ├── sample1.png
│   └── sample2.png
├── B/
│   └── ...
└── 0/
    └── ...
```

## 📖 Documentation

- [Installation & Quick Start](https://q-viper.github.io/text-baker/)
- [Examples & Code Samples](https://q-viper.github.io/text-baker/examples/)
- [Configuration Reference](https://q-viper.github.io/text-baker/configuration/)
- [CLI Reference](https://q-viper.github.io/text-baker/cli/)
- [API Reference](https://q-viper.github.io/text-baker/api/)

## 🧪 Development

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check . && ruff format .
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please fork, create a feature branch, and submit a PR.

## 👤 Author

**Ramkrishna Acharya** ([@q-viper](https://github.com/q-viper))

---

Built with [PySide6](https://doc.qt.io/qtforpython-6/), [OpenCV](https://opencv.org/), and [Typer](https://typer.tiangolo.com/)
