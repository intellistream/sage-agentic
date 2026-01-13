# Copilot (VS Code) Agent Instructions

## Scope
- This repo is the L3 agentic library `isage-agentic`.
- Python package import root: `sage_libs.sage_agentic` (namespace under `sage_libs`).
- Use src layout at `src/sage_libs/sage_agentic/`.

## Do / Don't
- Do keep imports under `sage_libs.sage_agentic.*`; avoid old `sage_agentic` root.
- Do not add dependencies on SAGE middleware or external services.
- Keep edits ASCII; brief comments only when clarifying non-obvious code.

## Common Tasks
- Install dev deps: `pip install -e .[dev]`.
- Lint (ruff default config in pyproject): `ruff check .`.
- Tests: `pytest tests/ -v` (currently no tests present).
- Import smoke test: `python - <<'PY'
from sage_libs.sage_agentic import agents, workflow
print('ok')
PY`

## Publishing (isage-pypi-publisher)
- Clean: `rm -rf dist build *.egg-info src/isage_agentic.egg-info`
- Build: `python -m build`
- TestPyPI: `isage-pypi-publisher --repository testpypi dist/*`
- PyPI: `isage-pypi-publisher dist/*`
- Bump versions in both `pyproject.toml` and `src/sage_libs/sage_agentic/__init__.py` for releases.

## Release Notes
- Current version: 0.1.0.0 (breaking namespace change).
- Ensure downstream import updates use `sage_libs.sage_agentic`.
