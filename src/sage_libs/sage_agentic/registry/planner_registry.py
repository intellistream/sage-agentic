"""Planner registry and factory."""

from __future__ import annotations

from collections.abc import Callable

from sage_libs.sage_agentic.interface.protocols import PlannerProtocol

_PLANNER_REGISTRY: dict[str, Callable[..., PlannerProtocol]] = {}


def register(name: str, factory: Callable[..., PlannerProtocol]) -> None:
    """Register a planner implementation.

    Args:
        name: Planner name
        factory: Factory function that creates planner instances
    """
    _PLANNER_REGISTRY[name] = factory


def create(name: str, **kwargs) -> PlannerProtocol:
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
