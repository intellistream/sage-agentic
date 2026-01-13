"""Agentic interfaces - Protocol definitions for external implementations.

This module defines the stable public API surface for agentic components.
Heavy implementations are in the external `isage-agentic` package.
"""

from . import agent, planner, tool_selector, workflow

__all__ = [
    "agent",
    "planner",
    "tool_selector",
    "workflow",
]
