"""Determinism and reproducibility utilities."""

from __future__ import annotations

import random


def set_seed(seed: int) -> None:
    """Set random seed for reproducibility.

    Args:
        seed: Random seed value
    """
    random.seed(seed)

    # Set numpy seed if available
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass

    # Set torch seed if available
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def get_seed() -> int | None:
    """Get current random seed state.

    Returns:
        Current seed if available, None otherwise
    """
    # Python's random doesn't expose seed directly,
    # so we return None
    return None


class DeterministicContext:
    """Context manager for deterministic execution."""

    def __init__(self, seed: int):
        self.seed = seed
        self.old_state = None

    def __enter__(self):
        # Save old random state
        self.old_state = random.getstate()

        # Set seed
        set_seed(self.seed)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old state
        if self.old_state:
            random.setstate(self.old_state)


__all__ = [
    "set_seed",
    "get_seed",
    "DeterministicContext",
]
