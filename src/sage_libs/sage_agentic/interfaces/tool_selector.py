"""Tool selector protocol definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    """Tool definition."""

    name: str
    description: str
    parameters: dict[str, Any]
    metadata: dict[str, Any] | None = None


class ToolSelector(ABC):
    """Base protocol for tool selection algorithms.

    Tool selectors choose relevant tools for a given query.
    """

    @abstractmethod
    def select(
        self,
        query: str,
        available_tools: list[Tool],
        k: int = 5,
        context: dict[str, Any] | None = None,
    ) -> list[Tool]:
        """Select top-k tools for the query.

        Args:
            query: User query or task description
            available_tools: Available tools
            k: Number of tools to select
            context: Optional context

        Returns:
            Selected tools ranked by relevance
        """
        pass


__all__ = [
    "Tool",
    "ToolSelector",
]
