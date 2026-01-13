"""Register built-in workflow optimizer implementations.

This module auto-registers all built-in workflow optimizers when imported.
External packages (isage-agentic) should register their own implementations.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_builtin_workflow_optimizers() -> None:
    """Register all built-in workflow optimizer implementations."""
    from sage_agentic.registry import workflow_registry

    # Import optimizer classes (all in optimizers/__init__.py)
    try:
        from sage_agentic.workflow.optimizers import (
            NoOpOptimizer,
            GreedyOptimizer,
            ParallelizationOptimizer,
        )

        # Register no-op optimizer (baseline)
        workflow_registry.register(
            "noop",
            lambda **kwargs: NoOpOptimizer(**kwargs),
        )
        # Also register as "baseline" alias
        workflow_registry.register(
            "baseline",
            lambda **kwargs: NoOpOptimizer(**kwargs),
        )
        logger.debug("Registered NoOpOptimizer")

        # Register greedy optimizer
        workflow_registry.register(
            "greedy",
            lambda **kwargs: GreedyOptimizer(**kwargs),
        )
        logger.debug("Registered GreedyOptimizer")

        # Register parallelization optimizer
        workflow_registry.register(
            "parallel",
            lambda **kwargs: ParallelizationOptimizer(**kwargs),
        )
        # Also register as "parallelization" alias
        workflow_registry.register(
            "parallelization",
            lambda **kwargs: ParallelizationOptimizer(**kwargs),
        )
        logger.debug("Registered ParallelizationOptimizer")

    except ImportError as e:
        logger.debug(f"Could not register workflow optimizers: {e}")


# Auto-register on import
register_builtin_workflow_optimizers()
