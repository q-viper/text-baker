# TextBaker Examples

This folder contains examples demonstrating how to use the TextBaker library.

## Examples

### `basic_generation.py`

Comprehensive example showing how to generate text images using the Python module:

- Basic text generation
- Texture application
- Background composition
- Transformations (rotation, perspective, scale, shear)
- Color customization
- Batch generation
- Config file usage

### `generate_icon.py`

Generate the TextBaker application icon with handwritten-style text using OpenCV.

### `generate_readme_images.py`

Generate the example images used in the README and documentation. Demonstrates:

- Different CV2 fonts (SIMPLEX, DUPLEX, TRIPLEX, SCRIPT_COMPLEX, etc.)
- Real assets from `assets/dataset/`, `assets/backgrounds/`, `assets/textures/`
- Various configurations: basic, transformed, colored, background, texture, full pipeline

## Running Examples

1. Make sure you have TextBaker installed:

```bash
# From the project root
pip install -e .
```

2. Run any example:

```bash
# Basic text generation examples
python examples/basic_generation.py

# Generate app icons
python examples/generate_icon.py

# Generate README example images
python examples/generate_readme_images.py
```

## Output

- `basic_generation.py` saves images to `examples/output/`
- `generate_icon.py` saves icons to `assets/`
- `generate_readme_images.py` saves images to `assets/readme/`

## Quick Reference

```python
from textbaker import TextGenerator
from textbaker.core.configs import (
    GeneratorConfig,
    DatasetConfig,
    TransformConfig,
    TextureConfig,
    BackgroundConfig,
)

# Create config
config = GeneratorConfig(
    seed=42,
    dataset=DatasetConfig(dataset_dir="assets/dataset"),
    texture=TextureConfig(enabled=True, texture_dir="assets/textures"),
    background=BackgroundConfig(enabled=True, background_dir="assets/backgrounds"),
)

# Generate
generator = TextGenerator(config)
result = generator.generate("Hello")

# Save
import cv2
cv2.imwrite("output.png", result.image)
```
