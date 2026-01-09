"""Planner protocol definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class PlanningContext:
    """Context for planning operations."""

    task: str
    available_tools: list[dict[str, Any]]
    constraints: dict[str, Any]
    history: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class Plan:
    """A plan produced by a planner."""

    steps: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None


class Planner(ABC):
    """Base protocol for planning algorithms.

    Planners decompose tasks into executable steps.
    """

    @abstractmethod
    def plan(self, context: PlanningContext) -> Plan:
        """Generate a plan for the given task.

        Args:
            context: Planning context with task and constraints

        Returns:
            Generated plan
        """
        pass

    @abstractmethod
    def replan(self, context: PlanningContext, failed_step: int) -> Plan:
        """Replan after a failure.

        Args:
            context: Current planning context
            failed_step: Index of failed step

        Returns:
            Updated plan
        """
        pass


__all__ = [
    "Planner",
    "PlanningContext",
    "Plan",
]
