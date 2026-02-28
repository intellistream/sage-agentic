"""Unit tests for AsyncReActLoop.

Covers:
- Normal completion (final_answer in first LLM response)
- Multi-step completion (tool call then final answer)
- Timeout / cancellation via asyncio.CancelledError
- Tool call failure degradation
- Streaming via run() async generator
- Max-steps guard
- Sync model (non-async generate) wrapped correctly
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sage_libs.sage_agentic.vida.async_react_loop import AsyncReActLoop


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_response(**kwargs: Any) -> str:
    """Return a JSON string with sensible defaults."""
    defaults = {
        "thought": "thinking",
        "action": "",
        "action_input": "",
        "observation": "",
        "final_answer": "",
    }
    defaults.update(kwargs)
    return json.dumps(defaults)


def _async_model(responses: list[str]) -> MagicMock:
    """Async LLM model that returns *responses* in order."""
    model = MagicMock()
    model.agenerate = AsyncMock(side_effect=responses)
    return model


def _sync_model(responses: list[str]) -> MagicMock:
    """Sync LLM model (has generate, not agenerate)."""
    model = MagicMock(spec=["generate"])
    model.generate = MagicMock(side_effect=responses)
    return model


def _make_async_tool(name: str, result: str | Exception) -> MagicMock:
    """Async tool that returns *result* (or raises if it's an Exception)."""
    tool = MagicMock()
    tool.name = name
    tool.description = f"tool {name}"
    if isinstance(result, Exception):
        tool.run = AsyncMock(side_effect=result)
    else:
        tool.run = AsyncMock(return_value=result)
    return tool


def _loop_with_no_delay(config: dict | None = None, **kwargs: Any) -> AsyncReActLoop:
    config = config or {}
    config.setdefault("step_delay", 0)
    config.setdefault("max_steps", 5)
    return AsyncReActLoop(config, **kwargs)


# ---------------------------------------------------------------------------
# 1. Normal completion (final_answer on first step)
# ---------------------------------------------------------------------------


class TestNormalCompletion:
    def test_run_with_tools_returns_final_answer(self) -> None:
        model = _async_model([_make_response(final_answer="42")])
        loop = _loop_with_no_delay(model=model)
        result = asyncio.run(loop.run_with_tools("What is 6×7?", [], {}))
        assert result == "42"

    def test_run_with_tools_sync_model(self) -> None:
        """Sync generate() model is auto-wrapped and works correctly."""
        model = _sync_model([_make_response(final_answer="hello")])
        loop = _loop_with_no_delay(model=model)
        result = asyncio.run(loop.run_with_tools("Say hello.", [], {}))
        assert result == "hello"

    def test_streaming_yields_tokens(self) -> None:
        model = _async_model([_make_response(thought="thinking fast", final_answer="42")])
        loop = _loop_with_no_delay(model=model)

        async def collect() -> list[str]:
            tokens: list[str] = []
            gen = await loop.run("What is 6×7?", [])
            async for tok in gen:
                tokens.append(tok)
            return tokens

        tokens = asyncio.run(collect())
        combined = "".join(tokens)
        assert "42" in combined
        assert "thinking fast" in combined


# ---------------------------------------------------------------------------
# 2. Multi-step tool call then final answer
# ---------------------------------------------------------------------------


class TestMultiStep:
    def test_tool_call_then_final_answer(self) -> None:
        tool = _make_async_tool("Calculator", "6")
        responses = [
            _make_response(action="Calculator", action_input="2+4"),
            _make_response(final_answer="the answer is 6"),
        ]
        model = _async_model(responses)
        loop = _loop_with_no_delay(model=model, tools=[tool])

        result = asyncio.run(loop.run_with_tools("What is 2+4?", [], {}))
        assert result == "the answer is 6"
        tool.run.assert_awaited_once_with("2+4")

    def test_per_call_tools_override(self) -> None:
        """Tools passed to run_with_tools() are visible even if not in constructor."""
        tool = _make_async_tool("Echo", "ECHO:hello")
        responses = [
            _make_response(action="Echo", action_input="hello"),
            _make_response(final_answer="done"),
        ]
        model = _async_model(responses)
        loop = _loop_with_no_delay(model=model)  # no tools in constructor

        result = asyncio.run(loop.run_with_tools("echo test", [tool], {}))
        assert result == "done"


# ---------------------------------------------------------------------------
# 3. Timeout / cancellation
# ---------------------------------------------------------------------------


class TestCancellation:
    def test_cancelled_error_propagates(self) -> None:
        """CancelledError raised mid-LLM-call bubbles up cleanly."""

        async def cancelling_agenerate(messages: list) -> str:
            raise asyncio.CancelledError()

        model = MagicMock()
        model.agenerate = cancelling_agenerate
        loop = _loop_with_no_delay(model=model)

        with pytest.raises(asyncio.CancelledError):
            asyncio.run(loop.run_with_tools("any query", [], {}))

    def test_timeout_cancels_loop(self) -> None:
        """asyncio.wait_for timeout cancels the loop and raises TimeoutError."""

        async def slow_agenerate(messages: list) -> str:
            await asyncio.sleep(100)  # never returns in test time
            return _make_response(final_answer="never")

        model = MagicMock()
        model.agenerate = slow_agenerate
        loop = _loop_with_no_delay(model=model)

        async def run_with_timeout() -> str:
            return await asyncio.wait_for(
                loop.run_with_tools("slow query", [], {}),
                timeout=0.05,
            )

        with pytest.raises((asyncio.TimeoutError, TimeoutError)):
            asyncio.run(run_with_timeout())


# ---------------------------------------------------------------------------
# 4. Tool call failure degradation
# ---------------------------------------------------------------------------


class TestToolFailureDegradation:
    def test_failing_tool_records_error_and_continues(self) -> None:
        """A tool that raises should produce an error observation; the loop
        continues and can still return a final answer."""
        failing_tool = _make_async_tool("Broken", ValueError("network error"))
        responses = [
            _make_response(action="Broken", action_input="x"),
            _make_response(final_answer="recovered"),
        ]
        model = _async_model(responses)
        loop = _loop_with_no_delay(model=model, tools=[failing_tool])

        result = asyncio.run(loop.run_with_tools("test degradation", [], {}))
        assert result == "recovered"

    def test_failing_tool_observation_contains_error_tag(self) -> None:
        """The scratchpad observation for a failed tool starts with [tool_error]."""
        captured_scratchpad: list[str] = []
        failing_tool = _make_async_tool("Bad", RuntimeError("boom"))

        # We intercept by checking what gets yielded in streaming mode
        model = _async_model([
            _make_response(action="Bad", action_input="y"),
            _make_response(final_answer="ok"),
        ])
        loop = _loop_with_no_delay(model=model, tools=[failing_tool])

        async def collect() -> list[str]:
            tokens: list[str] = []
            gen = await loop.run("test", [])
            async for tok in gen:
                tokens.append(tok)
                captured_scratchpad.append(tok)
            return tokens

        asyncio.run(collect())
        combined = "".join(captured_scratchpad)
        assert "[tool_error]" in combined


# ---------------------------------------------------------------------------
# 5. Max-steps guard
# ---------------------------------------------------------------------------


class TestMaxSteps:
    def test_returns_empty_string_when_max_steps_exceeded(self) -> None:
        """When the LLM keeps requesting actions without final_answer, the loop
        terminates after max_steps and returns ''."""
        tool = _make_async_tool("Loop", "still going")
        # Always returns an action, never a final_answer
        responses = [_make_response(action="Loop", action_input="x")] * 10
        model = _async_model(responses)
        loop = _loop_with_no_delay({"max_steps": 3, "step_delay": 0}, model=model, tools=[tool])

        result = asyncio.run(loop.run_with_tools("looping forever", [], {}))
        assert result == ""
        assert tool.run.await_count == 3


# ---------------------------------------------------------------------------
# 6. SageLibsBaseAgent interface compliance
# ---------------------------------------------------------------------------


class TestInterfaceCompliance:
    def test_plan_returns_list_of_agent_actions(self) -> None:
        from sage.libs.agentic.interface.base import AgentAction

        model = _async_model([_make_response(final_answer="plan result")])
        loop = _loop_with_no_delay(model=model)
        actions = loop.plan("some task", {})
        assert isinstance(actions, list)
        assert len(actions) == 1
        assert isinstance(actions[0], AgentAction)

    def test_execute_returns_agent_result(self) -> None:
        from sage.libs.agentic.interface.base import AgentResult

        model = _async_model([_make_response(final_answer="exec result")])
        loop = _loop_with_no_delay(model=model)
        result = loop.execute("some task")
        assert isinstance(result, AgentResult)
        assert "exec result" in result.output

    def test_reset_is_a_no_op(self) -> None:
        model = _async_model([])
        loop = _loop_with_no_delay(model=model)
        loop.reset()  # should not raise


# ---------------------------------------------------------------------------
# 7. Constructor validation
# ---------------------------------------------------------------------------


class TestConstructor:
    def test_requires_model(self) -> None:
        with pytest.raises(ValueError, match="model parameter is required"):
            AsyncReActLoop({})
