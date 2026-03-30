"""Regression tests for issue #11 API boundary cleanup."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_top_level_public_exports_no_interfaces_entry() -> None:
    import sage_libs.sage_agentic as sage_agentic

    assert "interfaces" not in sage_agentic.__all__
    assert "interface" in sage_agentic.__all__


def test_old_interfaces_module_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("sage_libs.sage_agentic.interfaces")


def test_workflow_registry_has_no_alias_keys() -> None:
    from sage_libs.sage_agentic.registry import workflow_registry

    registered = set(workflow_registry.registered())

    assert "noop" in registered
    assert "parallel" in registered
    assert "baseline" not in registered
    assert "parallelization" not in registered
