# Wave B3 Migration Guide (`sage-agentic#12`)

This document records the direct migration steps for the Wave B boundary changes.

## Scope

- Repository: `sage-agentic` (L3)
- Goal: keep L3 runtime/service-neutral and remove implicit cross-layer wiring
- Policy: direct removal, no alias layer, no re-export layer

## Breaking Changes

### 1) `LLMWorkflowGenerator` no longer imports `sage-cli`

`LLMWorkflowGenerator` now requires application-layer injection via `plan_generator`.

#### Before

```python
from sage_libs.sage_agentic.workflow.generators import LLMWorkflowGenerator

generator = LLMWorkflowGenerator(model="qwen-max")
result = generator.generate(context)
```

#### After

```python
from sage_libs.sage_agentic.workflow.generators import LLMWorkflowGenerator


def app_plan_generator(requirements: dict, config: dict) -> dict:
    return {
        "pipeline": {"name": "demo", "description": ""},
        "source": {"class": "sage.libs.foundation.io.source.FileSource", "params": {}, "summary": ""},
        "stages": [],
        "sink": {"class": "sage.libs.foundation.io.sink.TerminalSink", "params": {}, "summary": ""},
    }


generator = LLMWorkflowGenerator(
    model="qwen-max",
    api_key="<your-api-key>",
    plan_generator=app_plan_generator,
)
result = generator.generate(context)
```

### 2) Rule-based raw plan no longer uses `sage.middleware.*` class paths

Raw plan stage classes now use L3 paths under `sage.libs.rag.*`.

### 3) `BaseAgent` requires explicit `model` injection

`BaseAgent` no longer creates model clients from config fields.

#### Before

```python
agent = BaseAgent(config={"search_api_key": "...", "model_name": "..."})
```

#### After

```python
agent = BaseAgent(
    config={"search_api_key": "..."},
    model=your_llm_client,
)
```

## Failure Semantics

- Missing `plan_generator` returns a failed `GenerationResult` with explicit error.
- Missing model injection in `BaseAgent` raises `ValueError` immediately.

## Verification

- Contract tests: `tests/test_wave_b3_boundary_contract.py`
- Existing async loop tests remain valid: `tests/test_async_react_loop.py`
