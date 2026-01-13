"""Register built-in planner implementations.

This module auto-registers all built-in planners when imported.
External packages (isage-agentic) should register their own implementations.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_builtin_planners() -> None:
    """Register all built-in planner implementations."""
    from sage_agentic.registry import planner_registry

    # Import planner classes
    try:
        from sage_agentic.agents.planning.react_planner import ReActPlanner

        planner_registry.register(
            "react",
            lambda **kwargs: ReActPlanner(**kwargs),
        )
        logger.debug("Registered ReActPlanner")
    except ImportError as e:
        logger.debug(f"Could not register ReActPlanner: {e}")

    try:
        from sage_agentic.agents.planning.tot_planner import TreeOfThoughtsPlanner

        planner_registry.register(
            "tot",
            lambda **kwargs: TreeOfThoughtsPlanner(**kwargs),
        )
        planner_registry.register(
            "tree_of_thoughts",
            lambda **kwargs: TreeOfThoughtsPlanner(**kwargs),
        )
        logger.debug("Registered TreeOfThoughtsPlanner")
    except ImportError as e:
        logger.debug(f"Could not register TreeOfThoughtsPlanner: {e}")

    try:
        from sage_agentic.agents.planning.hierarchical_planner import (
            HierarchicalPlanner,
        )

        planner_registry.register(
            "hierarchical",
            lambda **kwargs: HierarchicalPlanner(**kwargs),
        )
        logger.debug("Registered HierarchicalPlanner")
    except ImportError as e:
        logger.debug(f"Could not register HierarchicalPlanner: {e}")

    try:
        from sage_agentic.agents.planning.simple_llm_planner import SimpleLLMPlanner

        planner_registry.register(
            "simple",
            lambda **kwargs: SimpleLLMPlanner(**kwargs),
        )
        planner_registry.register(
            "simple_llm",
            lambda **kwargs: SimpleLLMPlanner(**kwargs),
        )
        logger.debug("Registered SimpleLLMPlanner")
    except ImportError as e:
        logger.debug(f"Could not register SimpleLLMPlanner: {e}")


# Auto-register on import
register_builtin_planners()
