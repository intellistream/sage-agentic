"""Workflow registry and factory."""

from __future__ import annotations

from typing import Callable

from sage_agentic.interfaces.workflow import WorkflowOptimizer

_WORKFLOW_REGISTRY: dict[str, Callable[..., WorkflowOptimizer]] = {}


def register(name: str, factory: Callable[..., WorkflowOptimizer]) -> None:
    """Register a workflow optimizer implementation.

    Args:
        name: Optimizer name
        factory: Factory function that creates optimizer instances
    """
    _WORKFLOW_REGISTRY[name] = factory


def create(name: str, **kwargs) -> WorkflowOptimizer:
    """Create a workflow optimizer instance.

    Args:
        name: Optimizer name
        **kwargs: Optimizer-specific arguments

    Returns:
        WorkflowOptimizer instance

    Raises:
        KeyError: If optimizer not registered
    """
    if name not in _WORKFLOW_REGISTRY:
        raise KeyError(
            f"WorkflowOptimizer '{name}' not registered. "
            f"Available: {list(_WORKFLOW_REGISTRY.keys())}. "
            f"Install 'isage-agentic' package for implementations."
        )
    return _WORKFLOW_REGISTRY[name](**kwargs)


def registered() -> list[str]:
    """Get list of registered workflow optimizers.

    Returns:
        List of optimizer names
    """
    return list(_WORKFLOW_REGISTRY.keys())


__all__ = [
    "register",
    "create",
    "registered",
]
