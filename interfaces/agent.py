"""Agent and Bot protocol definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class AgentContext(Protocol):
    """Context passed to agents during execution."""

    task: str
    history: list[dict[str, Any]]
    metadata: dict[str, Any]


class Agent(ABC):
    """Base protocol for all agent implementations.

    Agents are autonomous systems that can perceive, reason, and act.
    """

    @abstractmethod
    def execute(self, task: str, context: AgentContext | None = None) -> Any:
        """Execute a task.

        Args:
            task: Task description
            context: Optional execution context

        Returns:
            Task result
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state."""
        pass


class Bot(ABC):
    """Base protocol for role-specific bots.

    Bots are specialized agents with specific roles (answer, critic, etc.).
    """

    @abstractmethod
    def process(self, input: str, context: dict[str, Any] | None = None) -> str:
        """Process input according to bot's role.

        Args:
            input: Input text
            context: Optional context

        Returns:
            Processed output
        """
        pass


__all__ = [
    "Agent",
    "AgentContext",
    "Bot",
]
