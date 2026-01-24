"""Register built-in tool selector implementations.

This module auto-registers all built-in tool selectors when imported.
External packages (isage-agentic) should register their own implementations.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_builtin_tool_selectors() -> None:
    """Register all built-in tool selector implementations."""
    from sage_libs.sage_agentic.registry import tool_selector_registry

    # Import selector classes
    try:
        from sage_libs.sage_agentic.agents.action.tool_selection.keyword_selector import (
            KeywordSelector,
        )

        tool_selector_registry.register(
            "keyword",
            lambda **kwargs: KeywordSelector(**kwargs),
        )
        logger.debug("Registered KeywordSelector")
    except ImportError as e:
        logger.debug(f"Could not register KeywordSelector: {e}")

    try:
        from sage_libs.sage_agentic.agents.action.tool_selection.embedding_selector import (
            EmbeddingSelector,
        )

        tool_selector_registry.register(
            "embedding",
            lambda **kwargs: EmbeddingSelector(**kwargs),
        )
        logger.debug("Registered EmbeddingSelector")
    except ImportError as e:
        logger.debug(f"Could not register EmbeddingSelector: {e}")

    try:
        from sage_libs.sage_agentic.agents.action.tool_selection.hybrid_selector import (
            HybridSelector,
        )

        tool_selector_registry.register(
            "hybrid",
            lambda **kwargs: HybridSelector(**kwargs),
        )
        logger.debug("Registered HybridSelector")
    except ImportError as e:
        logger.debug(f"Could not register HybridSelector: {e}")

    try:
        from sage_libs.sage_agentic.agents.action.tool_selection.dfsdt_selector import (
            DFSDTSelector,
        )

        tool_selector_registry.register(
            "dfsdt",
            lambda **kwargs: DFSDTSelector(**kwargs),
        )
        tool_selector_registry.register(
            "dfs_dt",
            lambda **kwargs: DFSDTSelector(**kwargs),
        )
        logger.debug("Registered DFSDTSelector")
    except ImportError as e:
        logger.debug(f"Could not register DFSDTSelector: {e}")

    try:
        from sage_libs.sage_agentic.agents.action.tool_selection.gorilla_selector import (
            GorillaSelector,
        )

        tool_selector_registry.register(
            "gorilla",
            lambda **kwargs: GorillaSelector(**kwargs),
        )
        logger.debug("Registered GorillaSelector")
    except ImportError as e:
        logger.debug(f"Could not register GorillaSelector: {e}")


# Auto-register on import
register_builtin_tool_selectors()
