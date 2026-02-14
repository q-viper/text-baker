# TextBaker 🍞

**Synthetic Text Dataset Generator for OCR Training**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

TextBaker is a Python-based tool for creating/generating synthetic images to train OCR (Optical Character Recognition) detection models. It provides a rich GUI application to compose synthetic text images with various transformations, backgrounds, and textures.

## Features

- 🎨 **Interactive GUI** - Easy-to-use graphical interface built with PySide6
- 📝 **Custom Text Generation** - Generate text from character datasets or custom pools
- 🔄 **Transformations** - Apply rotation, perspective, and scaling to characters
- 🖼️ **Background Compositing** - Overlay text on custom background images
- 🎭 **Texture Application** - Apply textures to characters or whole text
- 🎲 **Randomization** - Random character selection, positioning, and augmentation
- 💾 **Batch Export** - Save generated images for training datasets
- 🖥️ **Rich CLI** - Beautiful command-line interface with Typer

## Quick Start

```bash
# Install TextBaker
pip install textbaker

# Launch the GUI
textbaker

# Show help
textbaker --help
```

## Author

**Ramkrishna Acharya**

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rnkrsoft/textbaker/blob/main/LICENSE) file for details.
