# SIAS (Streaming Importance-Aware Agent System)

**Location**: `sage.libs.agentic.sias`  
**Layer**: L3 (Algorithm Library)  
**Role**: Internal reasoning + tool-selection support (importance-aware sampling)

## Purpose
- Agent-side reasoning for **tool selection** and **trajectory/sample importance**.
- Coreset-based selection and continual learning primitives to decide which tools/experiences to keep, replay, or prioritize.
- Pure L3: no control-plane/gateway/middleware deps; fail fast on missing resources.

## Components
- **CoresetSelector**: Importance-aware sample selection strategies (`core/coreset_selector.py`).
- **OnlineContinualLearner**: Replay buffer with importance weighting (`core/continual.py`).
- **StreamingImportanceScorer** (planned): SSIS prioritization for streaming traces.

## Usage
```python
from sage.libs.agentic.sias import CoresetSelector, OnlineContinualLearner

selector = CoresetSelector(strategy="hybrid")
selected = selector.select(samples, target_size=1000)

learner = OnlineContinualLearner(buffer_size=2048, replay_ratio=0.25)
batch = learner.update_buffer(new_samples)
```

## Design Principles
1. **L3 purity**: keep dependencies minimal; no control-plane/gateway/ports.
2. **Fail fast**: no silent fallbacks; surface errors when deps/config missing.
3. **Composable**: usable by agent planners/tool selectors and finetune routines.
4. **Extractable**: intended to be split into its own repo/package when ready.

## Relation to Agentic & Reasoning
- Complements `sage.libs.agentic.agents.action.tool_selection` by providing importance-aware selection logic.
- Can be composed with `sage.libs.agentic.reasoning` search/scoring primitives for richer decision policies.

## Migration Notes
- Keep public imports via `from sage.libs.agentic.sias import CoresetSelector, OnlineContinualLearner`.
- When extracted, update dependency to external `isage-sias` (planned) and keep this namespace as interface shim.
