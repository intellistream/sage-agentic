"""Async ReAct execution loop for VidaAgent.

This module provides ``AsyncReActLoop``, a fully-asynchronous implementation
of the ReAct (Reasoning + Acting) pattern.  It implements the L3 standard
``sage.libs.agentic.interface.base.BaseAgent`` interface.

Key capabilities
----------------
- ``run(query, context)`` — async generator that yields streamed tokens.
- ``run_with_tools(query, tools, memory_context)`` — single-shot async call
  that returns the final answer string.
- Graceful cancellation: ``asyncio.CancelledError`` propagates cleanly after
  the current tool call finishes.
- Tool-call failure degradation: a failing tool records the error as an
  observation and lets the loop continue rather than aborting.
- Max-steps guard to prevent infinite loops.

Layer note
----------
This file lives in ``sage-agentic`` (L3).  It imports from
``sage.libs.agentic.interface.base`` (also L3) — layer-compliant.
VidaAgent, VidaMemoryBridge, etc. live in ``sage-middleware`` (L4) and are
*not* imported here.

Example::

    loop = AsyncReActLoop(config, model=my_llm_client)
    async for token in loop.run("What is 2+2?", context=[]):
        print(token, end="", flush=True)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

# L3 → L3: sage.libs.agentic standard interface (compliant)
from sage.libs.agentic.interface.base import AgentAction, AgentResult
from sage.libs.agentic.interface.base import BaseAgent as SageLibsBaseAgent

__all__ = ["AsyncReActLoop", "AsyncTool"]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Async tool protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class AsyncTool(Protocol):
    """Minimal protocol for an async-capable tool."""

    name: str
    description: str

    async def run(self, input_: str) -> str:  # noqa: D102
        ...


# ---------------------------------------------------------------------------
# Internal step dataclass
# ---------------------------------------------------------------------------


@dataclass
class _ReActStep:
    thought: str = ""
    action: str = ""
    action_input: str = ""
    observation: str = ""
    final_answer: str = ""


# ---------------------------------------------------------------------------
# ReAct prompt templates (same format as sync BaseAgent)
# ---------------------------------------------------------------------------

_PREFIX = (
    "Answer the following questions as best you can. "
    "You have access to the following tools:{tool_names}"
)
_FORMAT_INSTRUCTIONS = """Always respond in the following JSON format:

```json
{{
  "thought": "your thought process",
  "action": "the action to take, should be one of [{tool_names}]",
  "action_input": "the input to the action",
  "observation": "Result from tool after execution",
  "final_answer": "Final answer to the original question"
}}
```
Notes:
If you are taking an action, set 'final_answer' to "" and 'observation' to "".
If you have enough information to answer, set 'action' to "", and fill in 'final_answer' directly.
"""
_SUFFIX = "Begin!\nQuestion: {input}\nThought:{agent_scratchpad}"


# ---------------------------------------------------------------------------
# AsyncReActLoop
# ---------------------------------------------------------------------------


class AsyncReActLoop(SageLibsBaseAgent):
    """Fully-async ReAct loop — implements the L3 standard BaseAgent interface.

    Args:
        config: Configuration dict.  Relevant keys:
            - ``max_steps`` (int, default 5): hard cap on reasoning iterations.
            - ``step_delay`` (float, default 0): seconds to sleep between steps
              (useful for rate-limited APIs; set to 0 in tests).
        model: LLM client with an async ``agenerate(messages)`` method **or**
            a sync ``generate(messages)`` method (wrapped automatically).
        tools: Optional list of ``AsyncTool`` objects to register.
            Tools can also be injected per-call via ``run_with_tools``.
        logger: Optional custom logger.

    Notes:
        - Implements ``sage.libs.agentic.interface.base.BaseAgent`` (L3 standard).
                - ``plan()`` and ``execute()`` provide the synchronous contract required
                    by ``SageLibsBaseAgent``.
    """

    def __init__(
        self,
        config: dict[str, Any],
        model: Any = None,
        tools: list[Any] | None = None,
        *,
        logger_: logging.Logger | None = None,
    ) -> None:
        if model is None:
            raise ValueError(
                "model parameter is required.  Inject an LLM client from the application layer "
                "to maintain L3 layer separation."
            )

        self._config = config
        self._model = model
        self._max_steps: int = config.get("max_steps", 5)
        self._step_delay: float = config.get("step_delay", 0.0)
        self._logger = logger_ or logging.getLogger(self.__class__.__name__)

        # Tools registry: {name: tool}
        self._tools: dict[str, Any] = {}
        for t in tools or []:
            self._tools[t.name] = t

    # ------------------------------------------------------------------
    # SageLibsBaseAgent (L3 standard) — mandatory abstract methods
    # ------------------------------------------------------------------

    def plan(self, task: str, context: dict[str, Any]) -> list[AgentAction]:
        """Run planning synchronously by executing the async loop to completion.

        Returns a single ``AgentAction`` wrapping the final answer.
        Works correctly whether or not an event loop is already running
        (e.g. plain scripts, pytest, Jupyter, FastAPI).
        """
        import concurrent.futures

        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        try:
            if running_loop is not None and running_loop.is_running():
                # Inside an existing event loop — run in a separate thread
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    future = ex.submit(asyncio.run, self.run_with_tools(task, [], {}))
                    answer = future.result()
            else:
                answer = asyncio.run(self.run_with_tools(task, [], {}))
        except Exception as exc:  # noqa: BLE001
            answer = f"[error] {exc}"
        return [AgentAction(tool_name="__final__", tool_input={}, thought=answer)]

    def execute(self, task: str, **kwargs: Any) -> AgentResult:
        """Execute task through the synchronous interface contract."""
        actions = self.plan(task, kwargs.get("context", {}))
        return AgentResult(
            output=actions[-1].thought if actions else "",
            intermediate_steps=[],
            metadata={},
        )

    def reset(self) -> None:
        """Reset transient state (no persistent state in this implementation)."""
        # Nothing to reset — stateless between calls.

    # ------------------------------------------------------------------
    # Primary async API
    # ------------------------------------------------------------------

    async def run(
        self,
        query: str,
        context: list[dict[str, Any]],
        *,
        extra_tools: list[Any] | None = None,
    ) -> AsyncIterator[str]:
        """Async ReAct loop that *yields* tokens as they arrive.

        Supports ``asyncio.CancelledError`` — the loop checks for cancellation
        before each LLM call and on each ``sleep`` boundary.

        Args:
            query: The user query to answer.
            context: Conversation history as ``[{"role": ..., "content": ...}]``.
            extra_tools: Additional tools available only for this call.

        Yields:
            Token strings as they are produced (thought, observation, answer).
        """
        return self._run_generator(query, context, extra_tools=extra_tools)

    async def run_with_tools(
        self,
        query: str,
        tools: list[Any],
        memory_context: dict[str, Any],
    ) -> str:
        """Single-shot async ReAct call returning the final answer.

        Args:
            query: The user query.
            tools: Per-call tools (merged with constructor tools).
            memory_context: Arbitrary context dict forwarded to the LLM prompt.

        Returns:
            The final answer string, or an empty string if max steps exceeded.
        """
        all_tools = dict(self._tools)
        for t in tools:
            all_tools[t.name] = t

        scratchpad = self._build_memory_prefix(memory_context)
        tool_names = ", ".join(all_tools.keys()) if all_tools else "(none)"
        prefix = _PREFIX.format(tool_names=tool_names)
        fmt = _FORMAT_INSTRUCTIONS.format(tool_names=tool_names)

        for step_idx in range(self._max_steps):
            # Cancellation checkpoint
            await asyncio.sleep(0)

            prompt_text = (
                prefix
                + fmt
                + _SUFFIX.format(input=query, agent_scratchpad=scratchpad)
            )
            messages = [{"role": "user", "content": prompt_text}]

            try:
                output_str = await self._call_model(messages)
            except asyncio.CancelledError:
                self._logger.info("AsyncReActLoop cancelled at step %d", step_idx)
                raise
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM call failed at step %d: %s", step_idx, exc)
                return ""

            try:
                output = self._parse_json(output_str)
            except ValueError as exc:
                self._logger.warning("JSON parse failed at step %d: %s", step_idx, exc)
                return ""

            if output.get("final_answer"):
                return str(output["final_answer"])

            action = output.get("action", "")
            action_input = output.get("action_input", "")

            if not action or action not in all_tools:
                self._logger.debug(
                    "No valid action at step %d (action=%r)", step_idx, action
                )
                return ""

            # Tool call — with failure degradation
            observation = await self._call_tool(all_tools[action], action_input)
            scratchpad += (
                str(output) + f"\nObservation: {observation}\nThought: "
            )

            if self._step_delay > 0:
                await asyncio.sleep(self._step_delay)

        self._logger.warning("Max steps (%d) exceeded for query: %r", self._max_steps, query)
        return ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_generator(
        self,
        query: str,
        context: list[dict[str, Any]],
        *,
        extra_tools: list[Any] | None = None,
    ) -> AsyncIterator[str]:
        """Actual async generator powering ``run()``."""
        all_tools = dict(self._tools)
        for t in extra_tools or []:
            all_tools[t.name] = t

        tool_names = ", ".join(all_tools.keys()) if all_tools else "(none)"
        prefix = _PREFIX.format(tool_names=tool_names)
        fmt = _FORMAT_INSTRUCTIONS.format(tool_names=tool_names)
        scratchpad = ""

        for step_idx in range(self._max_steps):
            await asyncio.sleep(0)  # cancellation checkpoint

            prompt_text = (
                prefix
                + fmt
                + _SUFFIX.format(input=query, agent_scratchpad=scratchpad)
            )
            messages = list(context) + [{"role": "user", "content": prompt_text}]

            try:
                output_str = await self._call_model(messages)
            except asyncio.CancelledError:
                self._logger.info("AsyncReActLoop stream cancelled at step %d", step_idx)
                raise

            yield f"[thought@step{step_idx}] "

            try:
                output = self._parse_json(output_str)
            except ValueError:
                yield "[parse_error]"
                return

            thought = output.get("thought", "")
            if thought:
                yield thought

            if output.get("final_answer"):
                yield "\n[answer] "
                yield str(output["final_answer"])
                return

            action = output.get("action", "")
            action_input = output.get("action_input", "")

            if not action or action not in all_tools:
                return

            yield f"\n[tool:{action}] "
            observation = await self._call_tool(all_tools[action], action_input)
            yield f"→ {observation}\n"
            scratchpad += str(output) + f"\nObservation: {observation}\nThought: "

            if self._step_delay > 0:
                await asyncio.sleep(self._step_delay)

    async def _call_model(self, messages: list[dict[str, Any]]) -> str:
        """Call the injected LLM model, supporting both async and sync clients."""
        if asyncio.iscoroutinefunction(getattr(self._model, "agenerate", None)):
            return await self._model.agenerate(messages)  # type: ignore[return-value]
        # Sync model — run in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._model.generate, messages)

    @staticmethod
    async def _call_tool(tool: Any, action_input: str) -> str:
        """Invoke a tool and return its observation string.

        Handles async tools, sync tools, and tool failures gracefully
        (failure degradation: returns an error string instead of raising).
        """
        try:
            if asyncio.iscoroutinefunction(getattr(tool, "run", None)):
                result = await tool.run(action_input)
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, tool.run, action_input)
            return str(result)
        except Exception as exc:  # noqa: BLE001
            return f"[tool_error] {exc}"

    @staticmethod
    def _build_memory_prefix(memory_context: dict[str, Any]) -> str:
        """Convert a memory_context dict into a scratchpad prefix string."""
        if not memory_context:
            return ""
        lines = [f"{k}: {v}" for k, v in memory_context.items()]
        return "Context:\n" + "\n".join(lines) + "\n\n"

    @staticmethod
    def _parse_json(output: str) -> dict[str, Any]:
        """Parse JSON from raw LLM output (plain or Markdown-fenced)."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON inside Markdown block: {exc}") from exc

        raise ValueError(
            "Invalid JSON format: no valid JSON found (plain or Markdown-fenced)"
        )
