"""Scoring, utility functions, and aggregation primitives.

Provides reusable scoring and aggregation functions for:
- Self-consistency voting
- Utility scoring
- Confidence aggregation
- Answer selection
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def majority_vote(responses: list[str]) -> str:
    """Select most common response (self-consistency voting).

    Args:
        responses: List of response strings

    Returns:
        Most common response
    """
    if not responses:
        raise ValueError("Cannot vote on empty list")

    counter = Counter(responses)
    return counter.most_common(1)[0][0]


def weighted_vote(responses: list[tuple[str, float]]) -> str:
    """Select response with highest weighted score.

    Args:
        responses: List of (response, weight) tuples

    Returns:
        Response with highest total weight
    """
    if not responses:
        raise ValueError("Cannot vote on empty list")

    scores: dict[str, float] = {}
    for response, weight in responses:
        scores[response] = scores.get(response, 0.0) + weight

    return max(scores.items(), key=lambda x: x[1])[0]


def aggregate_scores(scores: list[float], method: str = "mean") -> float:
    """Aggregate multiple scores using specified method.

    Args:
        scores: List of numeric scores
        method: Aggregation method ("mean", "max", "min", "median")

    Returns:
        Aggregated score
    """
    if not scores:
        raise ValueError("Cannot aggregate empty list")

    if method == "mean":
        return sum(scores) / len(scores)
    elif method == "max":
        return max(scores)
    elif method == "min":
        return min(scores)
    elif method == "median":
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        if n % 2 == 0:
            return (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        else:
            return sorted_scores[n // 2]
    else:
        raise ValueError(f"Unknown aggregation method: {method}")


def normalize_scores(scores: list[float], method: str = "minmax") -> list[float]:
    """Normalize scores to [0, 1] range.

    Args:
        scores: List of numeric scores
        method: Normalization method ("minmax" or "softmax")

    Returns:
        Normalized scores
    """
    if not scores:
        return []

    if method == "minmax":
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [1.0] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]
    elif method == "softmax":
        import math

        exp_scores = [math.exp(s) for s in scores]
        sum_exp = sum(exp_scores)
        return [e / sum_exp for e in exp_scores]
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def select_top_k(
    items: list[Any], scores: list[float], k: int, threshold: float | None = None
) -> list[Any]:
    """Select top-k items by score.

    Args:
        items: List of items to select from
        scores: Corresponding scores
        k: Number of items to select
        threshold: Optional minimum score threshold

    Returns:
        Top-k items (or fewer if threshold is applied)
    """
    if len(items) != len(scores):
        raise ValueError("Items and scores must have same length")

    # Zip items with scores and sort
    paired = list(zip(items, scores))
    paired.sort(key=lambda x: x[1], reverse=True)

    # Apply threshold if specified
    if threshold is not None:
        paired = [(item, score) for item, score in paired if score >= threshold]

    # Select top-k
    return [item for item, _ in paired[:k]]


__all__ = [
    "majority_vote",
    "weighted_vote",
    "aggregate_scores",
    "normalize_scores",
    "select_top_k",
]
