"""Agentic Interface Layer - Protocols, Registries, and Schemas.

This interface layer defines the contracts for agentic components.
Implementations are provided by the isage-agentic package.

Core Components:
- protocols: Abstract interfaces (Protocol/ABC) for planners, selectors, agents
- registries: Plugin registries for dynamic component loading  
- schemas: Data structures (Pydantic models) for requests/responses

Usage:
    from sage_agentic.interface import (
        PlannerProtocol, ToolSelectorProtocol, AgentProtocol,
        PlannerRegistry, SelectorRegistry,
        PlanRequest, PlanResult, ToolSelectionQuery
    )
"""

from .protocols import AgentProtocol, PlannerProtocol, ToolSelectorProtocol
from .registries import PlannerRegistry, SelectorRegistry
from .schemas import (
    PlanRequest,
    PlanResult,
    PlanStep,
    SelectorConfig,
    TimingDecision,
    TimingMessage,
    ToolMetadata,
    ToolPrediction,
    ToolSelectionQuery,
)

__all__ = [
    # Protocols
    "PlannerProtocol",
    "ToolSelectorProtocol",
    "AgentProtocol",
    # Registries
    "PlannerRegistry",
    "SelectorRegistry",
    # Schemas
    "PlanRequest",
    "PlanResult",
    "PlanStep",
    "ToolSelectionQuery",
    "ToolPrediction",
    "SelectorConfig",
    "TimingMessage",
    "TimingDecision",
    "ToolMetadata",
]
