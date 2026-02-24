# SAGE Agentic Copilot Instructions

## Scope
- Package: `isage-agentic`, import path `sage_libs.sage_agentic`.
- Layer: L3 algorithm library (pure agentic implementations).

## Critical rules
- Keep this package runtime/service-neutral; no L4+ dependencies (`sage-middleware`, `sage-kernel`).
- Do not add networked middleware resources (VDB/memory backends) here.
- No fallback logic; fail fast.
- Keep registry-based integration with SAGE factory via `_register.py`.

## Architecture focus
- SAGE `sage.libs.agentic` provides interfaces/factories.
- This repo provides concrete implementations (`ReAct`, planners, workflows, tools).
- Preserve clean boundaries between interface layer and implementations.

## Workflow
1. Make minimal changes under `src/sage_libs/sage_agentic/`.
2. Keep public imports stable unless explicitly changing API.
3. Run `pytest tests/ -v` and update README/docs for behavior changes.
