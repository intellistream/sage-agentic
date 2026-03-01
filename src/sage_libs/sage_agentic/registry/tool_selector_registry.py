"""Tool selector registry and factory."""

from __future__ import annotations

from collections.abc import Callable

from sage_libs.sage_agentic.interface.protocols import ToolSelectorProtocol

_TOOL_SELECTOR_REGISTRY: dict[str, Callable[..., ToolSelectorProtocol]] = {}


def register(name: str, factory: Callable[..., ToolSelectorProtocol]) -> None:
    """Register a tool selector implementation.

    Args:
        name: Tool selector name
        factory: Factory function that creates tool selector instances
    """
    _TOOL_SELECTOR_REGISTRY[name] = factory


def create(name: str, **kwargs) -> ToolSelectorProtocol:
    """Create a tool selector instance.

    Args:
        name: Tool selector name
        **kwargs: Tool selector-specific arguments

    Returns:
        ToolSelector instance

    Raises:
        KeyError: If tool selector not registered
    """
    if name not in _TOOL_SELECTOR_REGISTRY:
        raise KeyError(
            f"ToolSelector '{name}' not registered. "
            f"Available: {list(_TOOL_SELECTOR_REGISTRY.keys())}. "
            f"Install 'isage-agentic' package for implementations."
        )
    return _TOOL_SELECTOR_REGISTRY[name](**kwargs)


def registered() -> list[str]:
    """Get list of registered tool selectors.

    Returns:
        List of tool selector names
    """
    return list(_TOOL_SELECTOR_REGISTRY.keys())


__all__ = [
    "register",
    "create",
    "registered",
]
