# TextBaker 🍞

**Synthetic Text Dataset Generator for OCR Training**

TextBaker is a Python-based tool for creating/generating images to train OCR (Optical Character Recognition) detection models. It provides a GUI application to compose synthetic text images with various transformations, backgrounds, and textures.

## Features

- 🎨 **Interactive GUI** - Easy-to-use graphical interface built with PySide6
- 📝 **Custom Text Generation** - Generate text from character datasets or custom pools
- 🔄 **Transformations** - Apply rotation, perspective, and scaling to characters
- 🖼️ **Background Compositing** - Overlay text on custom background images
- 🎭 **Texture Application** - Apply textures to characters or whole text
- 🎲 **Randomization** - Random character selection, positioning, and augmentation
- 💾 **Batch Export** - Save generated images for training datasets

## Installation

### From PyPI (recommended)

```bash
pip install textbaker
```

### From Source

```bash
git clone https://github.com/rkacademy/textbaker.git
cd textbaker
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/rkacademy/textbaker.git
cd textbaker
pip install -e ".[dev]"
```

## Usage

### Command Line

After installation, you can run TextBaker from anywhere:

```bash
# Launch the GUI
textbaker

# Launch with specific folders
textbaker --dataset /path/to/dataset --output /path/to/output --backgrounds /path/to/backgrounds
```

### As Python Module

```bash
python -m textbaker
```

### In Python Code

```python
import textbaker as tb

# Use the image processor directly
processor = tb.ImageProcessor()
img = processor.load_and_process_image("character.png")

# Or launch the GUI application
from textbaker.app import DatasetMaker
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = DatasetMaker(
    dataset_root="/path/to/dataset",
    output_dir="/path/to/output"
)
window.show()
sys.exit(app.exec())
```

## Project Structure

```
textbaker/
├── __init__.py          # Package initialization, exports
├── __main__.py          # Entry point for python -m textbaker
├── cli.py               # Command-line interface
├── app/
│   ├── __init__.py
│   └── main_window.py   # Main GUI application window
├── core/
│   ├── __init__.py
│   └── image_processing.py  # Image manipulation utilities
├── widgets/
│   ├── __init__.py
│   ├── dialogs.py       # Dialog windows (texture picker, hints)
│   └── graphics.py      # Custom graphics items and views
└── utils/
    ├── __init__.py
    ├── logging.py       # Logging configuration
    └── helpers.py       # Helper functions
```

## Dataset Structure

Your character dataset should be organized as follows:

```
dataset/
├── A/
│   ├── img001.png
│   ├── img002.png
│   └── ...
├── B/
│   ├── img001.png
│   └── ...
├── 0/
│   ├── img001.png
│   └── ...
└── ...
```

Each subfolder name represents a character/label, containing image samples of that character.

## CLI Options

```
textbaker [OPTIONS]

Options:
  -d, --dataset PATH      Path to dataset folder containing character subfolders
  -o, --output PATH       Path to output folder for generated images
  -b, --backgrounds PATH  Path to folder containing background images
  -t, --textures PATH     Path to folder containing texture images
  -v, --version           Show version and exit
  -h, --help              Show help message and exit
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Mouse Wheel | Zoom in/out |
| Space + Drag | Pan view |
| Left Click | Select text item |
| Drag on text | Move text |
| Drag on blue circle | Rotate text |
| Drag on corners | Resize text |

## Requirements

- Python 3.9+
- numpy >= 1.21.0
- opencv-python >= 4.5.0
- PySide6 >= 6.4.0
- loguru >= 0.6.0

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Ramkrishna Acharya**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
