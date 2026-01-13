"""Evaluation & Profiling utilities (algorithmic level).

This module provides lightweight evaluation and telemetry helpers
for agents, retrievers, and planners. Full benchmarks live in L5 (sage-benchmark).

Components:
- metrics: Evaluation metrics (accuracy, F1, BLEU, etc.)
- telemetry: Telemetry schema and trace helpers
- determinism: Seed control and reproducibility utilities
"""

from . import determinism, metrics, telemetry

__all__ = [
    "metrics",
    "telemetry",
    "determinism",
]
