# Reasoning & Optimization Primitives

**Location**: `sage.libs.agentic.reasoning`  
**Layer**: L3 (Algorithm Library)  
**Dependencies**: Pure Python, no service dependencies

## Overview

This module provides generic search, optimization, and reasoning algorithms used by planners, agents, and other high-level components. These are pure algorithmic primitives that can be composed into higher-level systems.

## Components

### 1. Search Algorithms (`search.py`)

Generic search primitives for planning and reasoning:

- **BeamSearch**: Beam search with configurable beam width
- **DFSSearch**: Depth-first search
- **BFSSearch**: Breadth-first search
- **Future**: UCT, Monte Carlo Tree Search (MCTS)

**Usage**:
```python
from sage.libs.agentic.reasoning.search import BeamSearch

searcher = BeamSearch(beam_width=5)
path = searcher.search(
    initial_state=start,
    goal_fn=lambda s: s.is_goal(),
    expand_fn=lambda s: s.get_successors(),
    max_iterations=1000
)
```

### 2. Scoring & Aggregation (`scoring.py`)

Utility functions for scoring and aggregation:

- **majority_vote**: Self-consistency voting
- **weighted_vote**: Weighted voting
- **aggregate_scores**: Score aggregation (mean/max/min/median)
- **normalize_scores**: Score normalization (minmax/softmax)
- **select_top_k**: Top-k selection with optional threshold

**Usage**:
```python
from sage.libs.agentic.reasoning.scoring import majority_vote, normalize_scores

# Self-consistency voting
responses = ["Paris", "Paris", "London", "Paris"]
answer = majority_vote(responses)  # "Paris"

# Score normalization
scores = [0.5, 0.8, 0.3, 0.9]
normalized = normalize_scores(scores, method="softmax")
```

### 3. Constraints (Future)

Optional SMT/ILP hooks for constraint satisfaction (planned).

## Design Principles

1. **L3 Purity**: No control-plane, gateway, or middleware dependencies
2. **Pure Python**: Keep algorithms pure and testable
3. **Generic**: Algorithms should work with any state/domain
4. **Composable**: Can be combined into higher-level systems
5. **No Fallbacks**: Fail fast on missing resources

## Used By

- `sage.libs.agentic.agents.planning` - Planners (ToT, hierarchical)
- `sage.libs.agentic.workflow.optimizers` - Workflow optimization
- Custom agents and reasoning systems

## Future Enhancements

- UCT (Upper Confidence Trees)
- Monte Carlo Tree Search (MCTS)
- SMT/ILP constraint solving hooks
- Program synthesis primitives
- Symbolic reasoning utilities

## Migration Notes

This module consolidates search and optimization primitives previously scattered across:
- `sage.libs.agentic.agents.planning.utils`
- Various adhoc implementations in workflow optimizers

All search algorithms now use a unified `SearchAlgorithm` interface.
