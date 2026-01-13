# Workflow Core (Interfaces)

**Location**: `sage.libs.agentic.workflow`

Core abstractions and optimizers for agentic workflows:
- Graph/data model: `WorkflowGraph`, `WorkflowNode`, `NodeType`
- Constraints: budget, latency, quality (`constraints.py`)
- Optimizers: greedy/heuristic (`base.py`, `optimizers/`)
- Generators: rule-based & LLM-driven (`generators/`)
- Evaluation: `WorkflowEvaluator`

Principles:
- L3 purity (no control-plane/gateway deps)
- Fail fast (no silent fallbacks)
- Interfaces first; heavy presets live in `workflows/` or externalized
