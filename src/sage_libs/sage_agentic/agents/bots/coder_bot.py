"""
CoderBot - 代码生成 Bot

Layer: L3 (sage-agentic, pure algorithm)

核心编码推理循环：plan → generate → tool-call。
不直接依赖任何 L4+ 服务。LLM 后端、FS 工具均通过依赖注入传入。
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Protocol — 工具鸭子类型（不引入 L6 具体类）
# ---------------------------------------------------------------------------


@runtime_checkable
class WritableTool(Protocol):
    """Minimal tool interface CoderBot expects (duck-typed)."""

    name: str

    async def run(self, **kwargs: Any) -> Any: ...


# ---------------------------------------------------------------------------
# 提示模板（纯数据，L3 合规）
# ---------------------------------------------------------------------------

_PLAN_SYSTEM_PROMPT = """\
You are an expert software architect. Given a user's request, produce a JSON project plan.
The plan MUST be valid JSON with exactly this schema:

{
  "project_name": "<slug, lowercase-hyphen>",
  "description": "<one sentence>",
  "tech_stack": ["<item>", ...],
  "files": [
    {"path": "<relative path>", "description": "<what this file does>"},
    ...
  ]
}

Rules:
- project_name must be a valid directory name (no spaces).
- paths are relative to the project root, e.g. "backend/main.py".
- Include every file needed to run the project (README.md, requirements/package.json, source files, etc.).
- Respond with ONLY the JSON object, no markdown fences, no extra text.
"""

_FILE_SYSTEM_PROMPT = """\
You are an expert software engineer. Write the complete, production-ready content for ONE file.
- Output ONLY the raw file content with no markdown fences, no explanation.
- The file must be fully functional and consistent with the project context provided.
"""


def _plan_user_prompt(request: str) -> str:
    return f"User request: {request}\n\nProduce the project plan JSON."


def _file_user_prompt(request: str, plan: dict[str, Any], file_spec: dict[str, str]) -> str:
    other_files = [f["path"] for f in plan.get("files", []) if f["path"] != file_spec["path"]]
    return (
        f"Project: {plan.get('project_name', 'app')}\n"
        f"Description: {plan.get('description', '')}\n"
        f"Tech stack: {', '.join(plan.get('tech_stack', []))}\n"
        f"Other files in project: {', '.join(other_files[:10])}\n\n"
        f"Now write the complete content for: {file_spec['path']}\n"
        f"Purpose of this file: {file_spec.get('description', '')}\n\n"
        f"Original user request: {request}"
    )


# ---------------------------------------------------------------------------
# CoderBot
# ---------------------------------------------------------------------------

LLMCallable = Callable[[list[dict[str, str]]], Coroutine[Any, Any, str]]


class CoderBot:
    """Pure coding-strategy bot.

    Args:
        tools:        Iterable of tool objects exposing ``name`` and ``async run(**kwargs)``.
        llm_callable: Async callable ``(messages: list[dict]) -> str`` backed by any LLM.
                      Injected by the L6 caller so this bot stays L3-neutral.
        config:       Optional configuration dict.
    """

    def __init__(
        self,
        tools: list[Any],
        llm_callable: LLMCallable | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.tools: dict[str, Any] = {
            getattr(t, "name", str(i)): t for i, t in enumerate(tools)
        }
        self.llm_callable = llm_callable
        self.config = config or {}

    # ------------------------------------------------------------------
    # Public streaming interface
    # ------------------------------------------------------------------

    async def execute_stream(
        self, request: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Main entry point. Yields event dicts consumed by L6 CodingAgent.

        Event shapes
        ------------
        {"type": "plan_start"}
        {"type": "plan",        "plan": <dict>}
        {"type": "plan_error",  "error": <str>}
        {"type": "file_start",  "path": <str>, "index": <int>, "total": <int>}
        {"type": "file_ready",  "path": <str>, "bytes": <int>}
        {"type": "tool_start",  "tool": <str>, "path": <str>}
        {"type": "tool_result", "tool": <str>, "path": <str>, "result": <dict>}
        {"type": "done",        "project_name": <str>, "files_written": <int>}
        {"type": "error",       "error": <str>}
        """
        if self.llm_callable is None:
            yield {"type": "error", "error": "llm_callable not injected into CoderBot"}
            return

        # ---- 1. Plan -------------------------------------------------------
        yield {"type": "plan_start"}
        try:
            plan = await self._plan(request)
        except Exception as exc:
            logger.exception("CoderBot planning failed")
            yield {"type": "plan_error", "error": str(exc)}
            return

        yield {"type": "plan", "plan": plan}

        project_name: str = plan.get("project_name", "my-app")
        files: list[dict[str, str]] = plan.get("files", [])
        if not files:
            yield {"type": "error", "error": "LLM returned empty file list in plan"}
            return

        # ---- 2. Generate & write each file ---------------------------------
        files_written = 0
        for idx, file_spec in enumerate(files):
            path = file_spec.get("path", f"file_{idx}.txt")
            yield {"type": "file_start", "path": path, "index": idx, "total": len(files)}

            try:
                content = await self._generate_file(request, plan, file_spec)
            except Exception as exc:
                logger.warning("CoderBot: failed to generate %s: %s", path, exc)
                yield {"type": "error", "error": f"Failed to generate {path}: {exc}"}
                continue

            yield {"type": "file_ready", "path": path, "bytes": len(content.encode())}

            # ---- 3. Write via injected tool ---------------------------------
            write_tool = self.tools.get("file_write")
            if write_tool is None:
                logger.warning("CoderBot: 'file_write' tool not available, skipping write")
                continue

            yield {"type": "tool_start", "tool": "file_write", "path": path}
            try:
                result = await write_tool.run(
                    path=path, content=content, project=project_name
                )
                files_written += 1
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}

            yield {"type": "tool_result", "tool": "file_write", "path": path, "result": result}

        yield {"type": "done", "project_name": project_name, "files_written": files_written}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _plan(self, request: str) -> dict[str, Any]:
        """Ask LLM to produce a project plan as JSON."""
        messages = [
            {"role": "system", "content": _PLAN_SYSTEM_PROMPT},
            {"role": "user", "content": _plan_user_prompt(request)},
        ]
        raw = await self.llm_callable(messages)  # type: ignore[misc]
        raw = raw.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned invalid JSON plan: {exc}\n---\n{raw[:400]}") from exc

    async def _generate_file(
        self, request: str, plan: dict[str, Any], file_spec: dict[str, str]
    ) -> str:
        """Ask LLM to produce the full content of one file."""
        messages = [
            {"role": "system", "content": _FILE_SYSTEM_PROMPT},
            {"role": "user", "content": _file_user_prompt(request, plan, file_spec)},
        ]
        return await self.llm_callable(messages)  # type: ignore[misc]
