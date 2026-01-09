"""Reasoning & Optimization Primitives.

This module provides generic search, optimization, and reasoning algorithms
used by planners, agents, and other high-level components.

Components:
- search: Search algorithms (beam, DFS, BFS, UCT, Monte Carlo)
- scoring: Utility functions, aggregation, voting, self-consistency
- constraints: Optional SMT/ILP hooks for constraint satisfaction

These are pure algorithmic primitives with no service dependencies.
"""

from . import scoring, search

__all__ = [
    "search",
    "scoring",
]
