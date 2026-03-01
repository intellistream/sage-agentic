"""Boundary regression contract tests for Wave B3 (#12).

These tests guard L3 boundaries and breaking API changes introduced in Wave B2.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sage_libs.sage_agentic.agents.agent import BaseAgent
from sage_libs.sage_agentic.workflow.generators.base import GenerationContext
from sage_libs.sage_agentic.workflow.generators.llm_generator import LLMWorkflowGenerator
from sage_libs.sage_agentic.workflow.generators.rule_based_generator import (
    RuleBasedWorkflowGenerator,
)


def _repo_file(path: str) -> Path:
    return Path(__file__).resolve().parents[1] / path


def test_llm_generator_fails_without_plan_generator() -> None:
    generator = LLMWorkflowGenerator(api_key="token", base_url="http://localhost:8001/v1")
    result = generator.generate(GenerationContext(user_input="build a rag workflow"))

    assert result.success is False
    assert result.error is not None
    assert "plan_generator" in result.error


def test_llm_generator_uses_injected_plan_generator() -> None:
    captured: list[tuple[dict, dict]] = []

    def plan_generator(requirements: dict, config: dict) -> dict:
        captured.append((requirements, config))
        return {
            "pipeline": {"name": "demo", "description": "demo"},
            "source": {
                "class": "sage.libs.foundation.io.source.FileSource",
                "params": {"file_path": "demo.txt"},
                "summary": "source",
            },
            "stages": [
                {
                    "id": "s1",
                    "kind": "map",
                    "class": "sage.libs.rag.generators.OpenAIGenerator",
                    "params": {"model_name": "qwen"},
                    "summary": "gen",
                }
            ],
            "sink": {
                "class": "sage.libs.foundation.io.sink.TerminalSink",
                "params": {},
                "summary": "sink",
            },
        }

    generator = LLMWorkflowGenerator(
        model="qwen-max",
        api_key="token",
        base_url="http://localhost:8001/v1",
        plan_generator=plan_generator,
    )

    result = generator.generate(GenerationContext(user_input="build a rag workflow"))

    assert result.success is True
    assert len(captured) == 1
    requirements, config = captured[0]
    assert requirements["initial_prompt"] == "build a rag workflow"
    assert config["model"] == "qwen-max"
    assert config["backend"] == "openai"


def test_no_l5_or_l4_imports_in_llm_generator() -> None:
    content = _repo_file("src/sage_libs/sage_agentic/workflow/generators/llm_generator.py").read_text(
        encoding="utf-8"
    )

    assert "sage.cli" not in content
    assert "sage.middleware" not in content


def test_rule_based_raw_plan_uses_l3_paths_only() -> None:
    generator = RuleBasedWorkflowGenerator()
    context = GenerationContext(user_input="做一个问答检索流程")
    result = generator.generate(context)

    assert result.success is True
    assert result.raw_plan is not None

    class_paths = [stage["class"] for stage in result.raw_plan["stages"]]
    assert class_paths
    assert all(not item.startswith("sage.middleware.") for item in class_paths)


def test_base_agent_requires_model_injection() -> None:
    with pytest.raises(ValueError, match="Model parameter must be provided"):
        BaseAgent(config={"search_api_key": "fake-key"})
