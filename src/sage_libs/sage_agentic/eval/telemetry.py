"""Telemetry schema and trace helpers."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Span:
    """A single execution span for telemetry."""

    name: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    parent: Span | None = None
    children: list[Span] = field(default_factory=list)

    def end(self) -> None:
        """Mark span as ended."""
        self.end_time = time.time()

    def duration(self) -> float | None:
        """Get span duration in seconds."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time

    def add_child(self, child: Span) -> None:
        """Add child span."""
        child.parent = self
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration(),
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class Trace:
    """A collection of spans forming a trace."""

    name: str
    root_span: Span | None = None
    spans: list[Span] = field(default_factory=list)

    def start_span(self, name: str, parent: Span | None = None) -> Span:
        """Start a new span."""
        span = Span(name=name, parent=parent)

        if parent:
            parent.add_child(span)
        elif self.root_span is None:
            self.root_span = span

        self.spans.append(span)
        return span

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "root": self.root_span.to_dict() if self.root_span else None,
            "total_spans": len(self.spans),
        }


class SpanContext:
    """Context manager for spans."""

    def __init__(self, trace: Trace, name: str, parent: Span | None = None):
        self.trace = trace
        self.name = name
        self.parent = parent
        self.span: Span | None = None

    def __enter__(self) -> Span:
        self.span = self.trace.start_span(self.name, self.parent)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.end()
            if exc_type:
                self.span.metadata["error"] = str(exc_val)


__all__ = [
    "Span",
    "Trace",
    "SpanContext",
]
