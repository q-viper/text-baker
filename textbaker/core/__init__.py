"""TextBaker core package - image processing, configs, and definitions."""

from .configs import (
    DEFAULT_CONFIG,
    BackgroundConfig,
    BaseConfig,
    CharacterConfig,
    ColorConfig,
    DatasetConfig,
    GeneratorConfig,
    OutputConfig,
    TextureConfig,
    TransformConfig,
)
from .defs import (
    CharacterImage,
    ColorMode,
    ColorRange,
    GeneratedText,
    GenerationResult,
    TextureMode,
    TransformParams,
)
from .generator import TextGenerator

__all__ = [
    # Definitions
    "TextureMode",
    "ColorMode",
    "CharacterImage",
    "GeneratedText",
    "TransformParams",
    "ColorRange",
    "GenerationResult",
    # Configs
    "BaseConfig",
    "TransformConfig",
    "ColorConfig",
    "TextureConfig",
    "BackgroundConfig",
    "OutputConfig",
    "DatasetConfig",
    "CharacterConfig",
    "GeneratorConfig",
    "DEFAULT_CONFIG",
    # Generator
    "TextGenerator",
]
