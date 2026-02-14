"""
Random state management for reproducible generation.

Provides centralized control over randomness for reproducible dataset generation.
"""

import random
from collections.abc import Sequence
from typing import TypeVar

import numpy as np

T = TypeVar("T")

# Default seed for reproducibility
DEFAULT_SEED = 42


class RandomState:
    """
    Centralized random state manager for reproducible generation.

    Example:
        >>> from textbaker.utils import rng
        >>> rng.seed(42)
        >>> rng.randint(0, 100)
    """

    def __init__(self, seed: int = DEFAULT_SEED):
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        random.seed(seed)
        np.random.seed(seed)

    def seed(self, value: int) -> None:
        """Set random seed for reproducibility."""
        self._seed = value
        random.seed(value)
        np.random.seed(value)
        self._rng = np.random.default_rng(value)

    @property
    def current_seed(self) -> int:
        """Get current seed value."""
        return self._seed

    def randint(self, low: int, high: int) -> int:
        """Random integer in [low, high]."""
        return int(self._rng.integers(low, high + 1))

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        """Random float in [low, high)."""
        return float(self._rng.uniform(low, high))

    def choice(self, seq: Sequence[T]) -> T:
        """Random element from sequence."""
        if len(seq) == 0:
            raise IndexError("Cannot choose from empty sequence")
        return seq[int(self._rng.integers(0, len(seq)))]

    def choices(self, seq: Sequence[T], k: int = 1) -> list[T]:
        """K random elements with replacement."""
        indices = self._rng.integers(0, len(seq), size=k)
        return [seq[i] for i in indices]

    def shuffle(self, seq: list) -> None:
        """Shuffle list in place."""
        self._rng.shuffle(seq)


# Global instance with default seed
rng = RandomState(DEFAULT_SEED)
