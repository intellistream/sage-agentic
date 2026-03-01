# SAGE Agentic Copilot Instructions

## Scope
- Package: `isage-agentic`, import path `sage_libs.sage_agentic`.
- Layer: L3 algorithm library (pure agentic implementations).

## Critical rules
- Keep this package runtime/service-neutral; no L4+ dependencies (`sage-middleware`, `sage-kernel`).
- Do not create new local virtual environments (`venv`/`.venv`); use the existing configured Python environment.
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

## Polyrepo coordination (mandatory)

- This repository is an independent SAGE sub-repository and is developed/released independently.
- Do not assume sibling source directories exist locally in `intellistream/SAGE`.
- For cross-repo rollout, publish this repo/package first, then bump the version pin in `SAGE/packages/sage/pyproject.toml` when applicable.
- Do not add local editable installs of other SAGE sub-packages in setup scripts or docs.

## 🚫 NEVER_CREATE_DOT_VENV_MANDATORY

- 永远不要创建 `.venv` 或 `venv`（无任何例外）。
- NEVER create `.venv`/`venv` in this repository under any circumstance.
- 必须复用当前已配置的非-venv Python 环境（如现有 conda 环境）。
- If any script/task suggests creating a virtualenv, skip that step and continue with the existing environment.
