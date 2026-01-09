"""Workflow protocol definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Workflow node types."""

    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    RERANKING = "reranking"
    ANALYSIS = "analysis"
    CUSTOM = "custom"


@dataclass
class WorkflowNode:
    """A node in a workflow graph."""

    id: str
    node_type: NodeType
    config: dict[str, Any]
    cost: float = 0.0
    latency: float = 0.0
    quality: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """An edge in a workflow graph."""

    source: str
    target: str
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkflowGraph:
    """Workflow graph representation."""

    def __init__(self):
        self.nodes: dict[str, WorkflowNode] = {}
        self.edges: list[WorkflowEdge] = []

    def add_node(self, node: WorkflowNode) -> None:
        """Add a node to the workflow."""
        self.nodes[node.id] = node

    def add_edge(self, edge: WorkflowEdge) -> None:
        """Add an edge to the workflow."""
        self.edges.append(edge)

    def total_cost(self) -> float:
        """Calculate total workflow cost."""
        return sum(node.cost for node in self.nodes.values())

    def total_latency(self) -> float:
        """Calculate total workflow latency (critical path)."""
        # Simplified: return max node latency
        return max((node.latency for node in self.nodes.values()), default=0.0)


class WorkflowOptimizer(ABC):
    """Base protocol for workflow optimization algorithms."""

    @abstractmethod
    def optimize(
        self,
        workflow: WorkflowGraph,
        constraints: dict[str, Any],
    ) -> WorkflowGraph:
        """Optimize workflow under constraints.

        Args:
            workflow: Input workflow
            constraints: Optimization constraints (max_cost, max_latency, etc.)

        Returns:
            Optimized workflow
        """
        pass


__all__ = [
    "NodeType",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowGraph",
    "WorkflowOptimizer",
]
