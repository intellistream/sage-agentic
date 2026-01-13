"""Protocol definitions for agentic components.

Defines abstract interfaces using Python's Protocol and ABC.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol

# Use absolute imports to avoid relative path confusion
from sage_libs.sage_agentic.agents.action.tool_selection.schemas import (
    SelectorConfig,
    ToolPrediction,
    ToolSelectionQuery,
)
from sage_libs.sage_agentic.agents.planning.schemas import PlanRequest, PlanResult


class PlannerProtocol(Protocol):
    """Protocol for planner implementations.
    
    Planners generate step-by-step plans from high-level goals.
    """

    name: str

    def plan(self, request: PlanRequest) -> PlanResult:
        """Generate a task plan from a request.
        
        Args:
            request: PlanRequest containing goal, tools, and constraints
            
        Returns:
            PlanResult with generated steps
        """
        ...


class ToolSelectorProtocol(Protocol):
    """Protocol for tool selector implementations.
    
    Selectors choose relevant tools for a given query/context.
    """

    name: str

    def select(
        self, query: ToolSelectionQuery, top_k: Optional[int] = None
    ) -> list[ToolPrediction]:
        """Select top-k relevant tools for the given query.
        
        Args:
            query: Tool selection query
            top_k: Number of tools to select (overrides config if provided)
            
        Returns:
            List of tool predictions, sorted by score (descending)
        """
        ...


class AgentProtocol(Protocol):
    """Protocol for agent implementations.
    
    Agents orchestrate planning, tool selection, and execution.
    """

    def run(self, query: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute agent logic for a query.
        
        Args:
            query: User query or task description
            context: Optional context information
            
        Returns:
            Result dictionary with answer, steps, etc.
        """
        ...


# ABC versions for inheritance-based implementations

class BasePlanner(ABC):
    """Abstract base class for planners."""

    name: str = "base_planner"

    @abstractmethod
    def plan(self, request: PlanRequest) -> PlanResult:
        """Generate a task plan (must be implemented)."""
        ...


class BaseToolSelector(ABC):
    """Abstract base class for tool selectors."""

    name: str = "base_selector"

    @abstractmethod
    def select(
        self, query: ToolSelectionQuery, top_k: Optional[int] = None
    ) -> list[ToolPrediction]:
        """Select relevant tools (must be implemented)."""
        ...


class BaseAgent(ABC):
    """Abstract base class for agents."""

    @abstractmethod
    def run(self, query: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute agent logic (must be implemented)."""
        ...
