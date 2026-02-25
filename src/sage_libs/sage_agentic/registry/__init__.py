"""Agentic registries - Factory and registration system."""

# Auto-register built-in implementations
from . import (  # noqa: F401
    _register_planners,
    _register_tool_selectors,
    _register_workflows,
    planner_registry,
    tool_selector_registry,
    workflow_registry,
)

__all__ = [
    "planner_registry",
    "tool_selector_registry",
    "workflow_registry",
]
