"""Intent classification module for workflow routing.

Provides IntentClassifier, UserIntent enum, and IntentResult dataclass
for routing user queries to appropriate workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class UserIntent(str, Enum):
    """User intent categories for workflow routing."""

    GENERAL_CHAT = "general_chat"
    KNOWLEDGE_QUERY = "knowledge_query"
    SAGE_CODING = "sage_coding"
    SYSTEM_OPERATION = "system_operation"


@dataclass
class IntentResult:
    """Result of intent classification."""

    intent: UserIntent
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class IntentClassifier:
    """Intent classifier for routing user queries."""

    def __init__(self, mode: str = "keyword"):
        """Initialize intent classifier.

        Args:
            mode: Classification mode ("keyword" or "llm")
        """
        self.mode = mode

    async def classify(
        self, query: str, history: list[dict[str, Any]] | None = None
    ) -> IntentResult:
        """Classify user intent from query.

        Args:
            query: User query string
            history: Optional conversation history

        Returns:
            IntentResult with classified intent and confidence
        """
        query_lower = query.lower()
        history = history or []

        # Keyword-based classification
        if any(
            kw in query_lower
            for kw in [
                "sage",
                "pipeline",
                "operator",
                "stream",
                "kernel",
                "implement",
                "code",
                "function",
                "class",
                "api",
            ]
        ):
            return IntentResult(
                intent=UserIntent.SAGE_CODING,
                confidence=0.8,
                matched_keywords=["sage", "code"],
                metadata={"mode": self.mode},
            )

        if any(
            kw in query_lower
            for kw in [
                "what is",
                "how to",
                "explain",
                "describe",
                "tutorial",
                "documentation",
                "guide",
                "example",
                "learn",
            ]
        ):
            return IntentResult(
                intent=UserIntent.KNOWLEDGE_QUERY,
                confidence=0.85,
                matched_keywords=["knowledge", "query"],
                metadata={"mode": self.mode},
            )

        if any(
            kw in query_lower
            for kw in [
                "start",
                "stop",
                "restart",
                "run",
                "execute",
                "deploy",
                "install",
                "configure",
                "setup",
            ]
        ):
            return IntentResult(
                intent=UserIntent.SYSTEM_OPERATION,
                confidence=0.75,
                matched_keywords=["system", "operation"],
                metadata={"mode": self.mode},
            )

        # Default to general chat
        return IntentResult(
            intent=UserIntent.GENERAL_CHAT,
            confidence=0.6,
            matched_keywords=[],
            metadata={"mode": self.mode},
        )


__all__ = [
    "UserIntent",
    "IntentResult",
    "IntentClassifier",
]
