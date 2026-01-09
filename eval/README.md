# Evaluation & Profiling

**Location**: `sage.libs.agentic.eval`  
**Layer**: L3 (Algorithm Library)  
**Dependencies**: Pure Python, optional numpy/torch for seed control

## Overview

This module provides lightweight evaluation and telemetry helpers for agents, retrievers, and planners. Full benchmarks and experimental evaluation live in L5 (`sage-benchmark`).

## Components

### 1. Metrics (`metrics.py`)

Common evaluation metrics:

- **accuracy**: Classification accuracy
- **precision_recall_f1**: Precision, recall, F1 score
- **exact_match**: Exact match ratio
- **bleu_score**: Simple BLEU score (n-gram overlap)
- **mean_reciprocal_rank**: MRR for ranking tasks

**Usage**:
```python
from sage.libs.agentic.eval.metrics import accuracy, precision_recall_f1

# Classification metrics
predictions = [1, 0, 1, 1, 0]
targets = [1, 0, 0, 1, 0]

acc = accuracy(predictions, targets)  # 0.8
precision, recall, f1 = precision_recall_f1(predictions, targets, positive_label=1)

# Text generation metrics
from sage.libs.agentic.eval.metrics import bleu_score

pred = "The cat sat on the mat"
ref = "The cat is sitting on the mat"
score = bleu_score(pred, ref, n=4)
```

### 2. Telemetry (`telemetry.py`)

Span and trace helpers for profiling:

- **Span**: Single execution span with timing and metadata
- **Trace**: Collection of spans forming a trace
- **SpanContext**: Context manager for automatic span management

**Usage**:
```python
from sage.libs.agentic.eval.telemetry import Trace, SpanContext

trace = Trace(name="rag_pipeline")

with SpanContext(trace, "retrieval") as span:
    # Retrieval code
    span.metadata["docs_retrieved"] = 10

with SpanContext(trace, "generation") as span:
    # Generation code
    span.metadata["tokens_generated"] = 150

# Export trace
trace_dict = trace.to_dict()
```

### 3. Determinism (`determinism.py`)

Seed control and reproducibility utilities:

- **set_seed**: Set random seed (Python, numpy, torch)
- **get_seed**: Get current seed state
- **DeterministicContext**: Context manager for deterministic execution

**Usage**:
```python
from sage.libs.agentic.eval.determinism import set_seed, DeterministicContext

# Global seed
set_seed(42)

# Scoped determinism
with DeterministicContext(seed=42):
    # This block has deterministic random numbers
    result = some_random_operation()
```

## Design Principles

1. **Lightweight**: Minimal dependencies, no heavy ML libraries
2. **Reusable**: Metrics can be used across different evaluation scenarios
3. **Composable**: Telemetry spans can be nested
4. **L3 Scope**: Algorithmic-level evaluation, not full benchmarks
5. **Fail Fast**: No silent fallbacks

## Used By

- `sage.benchmark` (L5) - Full benchmark suites
- `sage.libs.agentic` - Agent evaluation
- `sage.libs.rag` - RAG quality metrics
- Custom evaluation scripts

## Relationship with sage-benchmark (L5)

| Component | L3 (sage.libs.agentic.eval) | L5 (sage-benchmark) |
|-----------|---------------------|---------------------|
| **Scope** | Reusable metrics & telemetry | Full benchmark suites & experiments |
| **Metrics** | Individual metric functions | Composite evaluation frameworks |
| **Telemetry** | Span/trace helpers | Full observability stack |
| **Data** | No data management | Dataset management, results storage |
| **Reports** | Raw metrics | Visualization, comparison, reports |

**Rule**: Use L3 for individual metric calculations; use L5 for end-to-end benchmarking.

## Future Enhancements

- More NLP metrics (ROUGE, METEOR, BERTScore)
- Ranking metrics (NDCG, MAP)
- Statistical significance tests
- Performance profiling helpers
- Reference trace comparisons

## Migration Notes

This module consolidates evaluation utilities previously scattered across:
- `sage.benchmark.common` - Moved heavy benchmarking to L5
- Various adhoc metric calculations
- Telemetry helpers from agent runtime

All metrics now follow consistent function signatures and return types.
