"""
Definitions, enums, and dataclasses for TextBaker.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np


class TextureMode(str, Enum):
    """Texture application mode."""

    NONE = "none"
    PER_CHAR = "per_char"
    WHOLE_TEXT = "whole_text"


class ColorMode(str, Enum):
    """Color application mode."""

    ORIGINAL = "original"
    RANDOM = "random"
    FIXED = "fixed"


@dataclass
class CharacterImage:
    """Represents a character image with metadata."""

    path: Path
    label: str
    image: Optional[np.ndarray] = None

    def load(self) -> np.ndarray:
        """Load the image from disk."""
        import cv2

        self.image = cv2.imread(str(self.path), cv2.IMREAD_UNCHANGED)
        return self.image


@dataclass
class GeneratedText:
    """Represents generated text with its images and labels."""

    text: str
    labels: list[str] = field(default_factory=list)
    images: list[np.ndarray] = field(default_factory=list)
    composite: Optional[np.ndarray] = None

    def __len__(self) -> int:
        return len(self.text)


@dataclass
class TransformParams:
    """Parameters for image transformation."""

    rotation: tuple[float, float] = (0.0, 0.0)
    perspective: tuple[float, float] = (0.0, 0.0)
    scale: tuple[float, float] = (1.0, 1.0)

    def copy(self) -> "TransformParams":
        return TransformParams(
            rotation=self.rotation, perspective=self.perspective, scale=self.scale
        )


@dataclass
class ColorRange:
    """RGB color range for random coloring."""

    r: tuple[int, int] = (0, 255)
    g: tuple[int, int] = (0, 255)
    b: tuple[int, int] = (0, 255)

    def as_tuple(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        return (self.r, self.g, self.b)


@dataclass
class GenerationResult:
    """Result of text generation."""

    image: np.ndarray
    text: str
    labels: list[str]
    seed: int
    params: dict = field(default_factory=dict)
