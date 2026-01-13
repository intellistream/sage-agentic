"""Search algorithms for planning and reasoning.

Provides generic search primitives used by planners and agents:
- Beam search
- Depth-first search (DFS)
- Breadth-first search (BFS)
- Upper Confidence Trees (UCT)
- Monte Carlo Tree Search (MCTS)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class SearchNode(Generic[T]):
    """A node in the search tree."""

    state: T
    parent: SearchNode[T] | None = None
    children: list[SearchNode[T]] | None = None
    score: float = 0.0
    visits: int = 0

    def __post_init__(self):
        if self.children is None:
            self.children = []


class SearchAlgorithm(ABC, Generic[T]):
    """Base class for search algorithms."""

    @abstractmethod
    def search(
        self,
        initial_state: T,
        goal_fn: callable,
        expand_fn: callable,
        max_iterations: int = 1000,
    ) -> list[T]:
        """Search for a path from initial_state to goal.

        Args:
            initial_state: Starting state
            goal_fn: Function that returns True if state is goal
            expand_fn: Function that returns list of successor states
            max_iterations: Maximum search iterations

        Returns:
            List of states forming a path to goal, or empty list if not found
        """
        pass


class BeamSearch(SearchAlgorithm[T]):
    """Beam search with configurable beam width."""

    def __init__(self, beam_width: int = 5):
        self.beam_width = beam_width

    def search(
        self,
        initial_state: T,
        goal_fn: callable,
        expand_fn: callable,
        max_iterations: int = 1000,
    ) -> list[T]:
        """Perform beam search."""
        beam = [SearchNode(state=initial_state)]

        for _ in range(max_iterations):
            if goal_fn(beam[0].state):
                return self._extract_path(beam[0])

            # Expand all nodes in current beam
            candidates = []
            for node in beam:
                successors = expand_fn(node.state)
                for state in successors:
                    child = SearchNode(state=state, parent=node)
                    candidates.append(child)

            if not candidates:
                break

            # Keep top beam_width candidates
            beam = sorted(candidates, key=lambda n: n.score, reverse=True)[
                : self.beam_width
            ]

        return []

    def _extract_path(self, node: SearchNode[T]) -> list[T]:
        """Extract path from root to node."""
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))


class DFSSearch(SearchAlgorithm[T]):
    """Depth-first search."""

    def search(
        self,
        initial_state: T,
        goal_fn: callable,
        expand_fn: callable,
        max_iterations: int = 1000,
    ) -> list[T]:
        """Perform DFS."""
        stack = [SearchNode(state=initial_state)]
        visited = set()
        iterations = 0

        while stack and iterations < max_iterations:
            iterations += 1
            node = stack.pop()

            if goal_fn(node.state):
                return self._extract_path(node)

            state_id = id(node.state)
            if state_id in visited:
                continue
            visited.add(state_id)

            successors = expand_fn(node.state)
            for state in successors:
                child = SearchNode(state=state, parent=node)
                stack.append(child)

        return []

    def _extract_path(self, node: SearchNode[T]) -> list[T]:
        """Extract path from root to node."""
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))


class BFSSearch(SearchAlgorithm[T]):
    """Breadth-first search."""

    def search(
        self,
        initial_state: T,
        goal_fn: callable,
        expand_fn: callable,
        max_iterations: int = 1000,
    ) -> list[T]:
        """Perform BFS."""
        from collections import deque

        queue = deque([SearchNode(state=initial_state)])
        visited = set()
        iterations = 0

        while queue and iterations < max_iterations:
            iterations += 1
            node = queue.popleft()

            if goal_fn(node.state):
                return self._extract_path(node)

            state_id = id(node.state)
            if state_id in visited:
                continue
            visited.add(state_id)

            successors = expand_fn(node.state)
            for state in successors:
                child = SearchNode(state=state, parent=node)
                queue.append(child)

        return []

    def _extract_path(self, node: SearchNode[T]) -> list[T]:
        """Extract path from root to node."""
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))


__all__ = [
    "SearchNode",
    "SearchAlgorithm",
    "BeamSearch",
    "DFSSearch",
    "BFSSearch",
]
