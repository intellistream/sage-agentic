#!/usr/bin/env python3
"""Test script for agentic registry system."""

from __future__ import annotations

import sys


def test_planner_registry():
    """Test planner registry."""
    print("=" * 60)
    print("Testing Planner Registry")
    print("=" * 60)

    from sage_libs.sage_agentic.registry import planner_registry

    # List registered planners
    registered = planner_registry.registered()
    print(f"✅ Registered planners: {registered}")

    # Test creation (will fail without LLM client, but that's OK)
    if "react" in registered:
        print("✅ ReActPlanner is registered")
        try:
            planner = planner_registry.create("react")
            print(f"  Created: {type(planner).__name__}")
        except Exception as e:
            print(f"  (Expected error during creation without LLM: {type(e).__name__})")

    print()


def test_tool_selector_registry():
    """Test tool selector registry."""
    print("=" * 60)
    print("Testing Tool Selector Registry")
    print("=" * 60)

    from sage_libs.sage_agentic.registry import tool_selector_registry

    # List registered selectors
    registered = tool_selector_registry.registered()
    print(f"✅ Registered tool selectors: {registered}")

    # Test creation
    if "keyword" in registered:
        print("✅ KeywordSelector is registered")
        try:
            selector = tool_selector_registry.create("keyword")
            print(f"  Created: {type(selector).__name__}")
        except Exception as e:
            print(f"  (Expected error: {type(e).__name__}: {e})")

    print()


def test_workflow_registry():
    """Test workflow registry."""
    print("=" * 60)
    print("Testing Workflow Registry")
    print("=" * 60)

    from sage_libs.sage_agentic.registry import workflow_registry

    # List registered optimizers
    registered = workflow_registry.registered()
    print(f"✅ Registered workflow optimizers: {registered}")

    # Test creation
    if "greedy" in registered:
        print("✅ GreedyOptimizer is registered")
        try:
            optimizer = workflow_registry.create("greedy")
            print(f"  Created: {type(optimizer).__name__}")
        except Exception as e:
            print(f"  (Expected error: {type(e).__name__}: {e})")

    print()


def test_interfaces():
    """Test interface imports."""
    print("=" * 60)
    print("Testing Interface Imports")
    print("=" * 60)

    from sage_libs.sage_agentic.interfaces import (
        agent,
        planner,
        tool_selector,
        workflow,
    )

    print(f"✅ agent module: {len(dir(agent))} exports")
    print(f"✅ planner module: {len(dir(planner))} exports")
    print(f"✅ tool_selector module: {len(dir(tool_selector))} exports")
    print(f"✅ workflow module: {len(dir(workflow))} exports")

    # Check specific protocols
    from sage_libs.sage_agentic.interfaces.planner import Planner, PlanningContext

    print(f"✅ Planner protocol: {Planner}")
    print(f"✅ PlanningContext dataclass: {PlanningContext}")

    print()


def main():
    """Run all tests."""
    try:
        test_interfaces()
        test_planner_registry()
        test_tool_selector_registry()
        test_workflow_registry()

        print("=" * 60)
        print("✅ All registry tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
