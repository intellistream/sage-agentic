"""Planner registry and factory."""

from __future__ import annotations

from typing import Callable

from sage_agentic.interfaces.planner import Planner

_PLANNER_REGISTRY: dict[str, Callable[..., Planner]] = {}


def register(name: str, factory: Callable[..., Planner]) -> None:
    """Register a planner implementation.

    Args:
        name: Planner name
        factory: Factory function that creates planner instances
    """
    _PLANNER_REGISTRY[name] = factory


def create(name: str, **kwargs) -> Planner:
    """Create a planner instance.

    Args:
        name: Planner name
        **kwargs: Planner-specific arguments

    Returns:
        Planner instance

    Raises:
        KeyError: If planner not registered
    """
    if name not in _PLANNER_REGISTRY:
        raise KeyError(
            f"Planner '{name}' not registered. Available: {list(_PLANNER_REGISTRY.keys())}. "
            f"Install 'isage-agentic' package for implementations."
        )
    return _PLANNER_REGISTRY[name](**kwargs)


def registered() -> list[str]:
    """Get list of registered planners.

    Returns:
        List of planner names
    """
    return list(_PLANNER_REGISTRY.keys())


__all__ = [
    "register",
    "create",
    "registered",
]
