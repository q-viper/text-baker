"""
TextBaker - Synthetic Text Dataset Generator for OCR Training

A Python-based tool for creating/generating images to train OCR detection models.

Usage as GUI Application:
    ```python
    import textbaker as tb
    tb.run_app()
    ```

Usage as Library:
    ```python
    from textbaker import TextGenerator, GeneratorConfig, TransformConfig

    # Create config
    config = GeneratorConfig(
        seed=42,
        spacing=5,
        transform=TransformConfig(rotation_range=(-15, 15)),
    )

    # Generate images programmatically
    generator = TextGenerator(config)
    result = generator.generate("hello")
    generator.save(result)

    # Or generate random text
    result = generator.generate_random(length=5)
    ```

Author: Ramkrishna Acharya
Repository: https://github.com/q-viper/text-baker
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("textbaker")
except PackageNotFoundError:
    __version__ = "0.1.0"

__author__ = "Ramkrishna Acharya"
__description__ = "Synthetic Text Dataset Generator for OCR Training"

# Import rng for convenience
from textbaker.core.configs import (
    DEFAULT_CONFIG,
    BackgroundConfig,
    CharacterConfig,
    ColorConfig,
    DatasetConfig,
    GeneratorConfig,
    OutputConfig,
    TextureConfig,
    TransformConfig,
)

# Import core components for library usage
from textbaker.core.defs import (
    CharacterImage,
    ColorMode,
    ColorRange,
    GeneratedText,
    GenerationResult,
    TextureMode,
    TransformParams,
)
from textbaker.core.generator import TextGenerator
from textbaker.utils.random_state import rng


def run_app():
    """Run the TextBaker GUI application."""
    import sys

    from PySide6.QtWidgets import QApplication

    from textbaker.app.main_window import DatasetMaker

    app = QApplication(sys.argv)
    window = DatasetMaker()
    window.show()
    sys.exit(app.exec())


# Lazy imports for backwards compatibility
def __getattr__(name):
    if name == "DatasetMaker":
        from textbaker.app.main_window import DatasetMaker

        return DatasetMaker
    elif name == "ImageProcessor":
        from textbaker.core.image_processing import ImageProcessor

        return ImageProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Random state
    "rng",
    # App
    "run_app",
    "DatasetMaker",
    "ImageProcessor",
    # Generator
    "TextGenerator",
    # Configs
    "GeneratorConfig",
    "TransformConfig",
    "ColorConfig",
    "TextureConfig",
    "BackgroundConfig",
    "OutputConfig",
    "DatasetConfig",
    "CharacterConfig",
    "DEFAULT_CONFIG",
    # Definitions
    "TextureMode",
    "ColorMode",
    "CharacterImage",
    "GeneratedText",
    "TransformParams",
    "ColorRange",
    "GenerationResult",
]
