from __future__ import annotations

import asyncio
from typing import Any

from sage_libs.sage_agentic.agents.bots.searcher_bot import SearcherBot


class _GoodTool:
    tool_name = "good_tool"

    def execute(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"content": query, "extra": kwargs.get("extra")}]


class _RunOnlyTool:
    tool_name = "run_only"

    async def run(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"content": query, "extra": kwargs.get("extra")}]


class _NoNameTool:
    def execute(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"content": query, "extra": kwargs.get("extra")}]


def test_searcher_bot_uses_execute_only() -> None:
    bot = SearcherBot(tools=[_GoodTool()])
    results = asyncio.run(bot.search("hello", extra="x"))

    assert len(results) == 1
    assert results[0]["source"] == "good_tool"
    assert results[0]["content"] == "hello"
    assert results[0]["extra"] == "x"


def test_searcher_bot_rejects_tool_without_execute() -> None:
    bot = SearcherBot(tools=[_RunOnlyTool()])

    async def _collect() -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        async for event in bot.search_generator("hello"):
            events.append(event)
        return events

    events = asyncio.run(_collect())

    assert len(events) == 2
    assert events[0]["type"] == "tool_start"
    assert events[1] == {
        "type": "tool_error",
        "tool": "run_only",
        "error": "Tool missing required 'execute' method",
    }


def test_searcher_bot_rejects_tool_without_tool_name() -> None:
    bot = SearcherBot(tools=[_NoNameTool()])

    async def _collect() -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        async for event in bot.search_generator("hello"):
            events.append(event)
        return events

    events = asyncio.run(_collect())

    assert events == [
        {
            "type": "tool_error",
            "tool": "Unknown Tool",
            "error": "Tool missing required 'tool_name' attribute",
        }
    ]
