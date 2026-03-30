"""
SearcherBot - 搜索Bot

负责执行信息检索任务，协调多个搜索工具（如 Arxiv, Google Search, Internal Knowledge 等）。
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sage.libs.foundation.tools.tool import BaseTool

logger = logging.getLogger(__name__)


class SearcherBot:
    """
    SearcherBot - 用于执行搜索任务的Agent Bot

    它接收一组工具，并根据查询并行（或串行）调用这些工具，
    最后聚合结果返回。
    """

    def __init__(
        self, tools: list[BaseTool], config: dict[str, Any] | None = None, ctx: Any | None = None
    ):
        """
        初始化SearcherBot

        Args:
            tools: 可用的搜索工具列表
            config: 配置字典
            ctx: 上下文对象
        """
        self.tools = tools
        self.config = config or {}
        self.ctx = ctx

    async def search_generator(self, query: str, **kwargs) -> AsyncGenerator[dict[str, Any], None]:
        """
        执行搜索并流式返回事件 (Async Generator)

        Yields:
            Dict: 事件字典，包含 type, tool, result 等字段
        """
        logger.info(
            f"SearcherBot executing search for query: '{query}' with {len(self.tools)} tools"
        )

        for tool in self.tools:
            tool_name = "Unknown Tool"
            try:
                tool_name = getattr(tool, "tool_name", "")
                if not tool_name:
                    tool_name = "Unknown Tool"
                    raise ValueError("Tool missing required 'tool_name' attribute")
                logger.debug(f"Invoking tool: {tool_name}")

                # Yield start event
                yield {"type": "tool_start", "tool": tool_name, "status": "running"}

                # 构造调用参数
                call_kwargs = kwargs.copy()

                # 检查工具元数据 (如果可用)
                input_types = getattr(tool, "input_types", {})

                # 如果是字典形式的 input_types，检查是否有 query 字段
                has_query_param = False
                if isinstance(input_types, dict):
                    if "query" in input_types or "search_query" in input_types:
                        has_query_param = True

                # 针对已知工具的特殊处理
                if "Nature" in tool_name and not has_query_param:
                    if "nature" in query.lower() or "news" in query.lower():
                        # 尝试调用
                        pass
                    else:
                        yield {
                            "type": "tool_skip",
                            "tool": tool_name,
                            "reason": "Query not relevant",
                        }
                        continue

                # 执行工具调用（L3: execute）
                if not hasattr(tool, "execute") or not callable(tool.execute):
                    logger.warning(f"Tool {tool_name} has no 'execute' method")
                    yield {
                        "type": "tool_error",
                        "tool": tool_name,
                        "error": "Tool missing required 'execute' method",
                    }
                    continue

                result = tool.execute(query=query, **call_kwargs)

                # 规范化结果
                if result:
                    # L6 工具可能返回 dict with 'result' key
                    if isinstance(result, dict) and "status" in result and "result" in result:
                        if result["status"] == "success":
                            result = result["result"]
                        else:
                            logger.warning(
                                f"Tool {tool_name} returned error: {result.get('error')}"
                            )
                            yield {
                                "type": "tool_error",
                                "tool": tool_name,
                                "error": result.get("error"),
                            }
                            continue

                    normalized = self._normalize_result(tool_name, result)

                    yield {
                        "type": "tool_result",
                        "tool": tool_name,
                        "results": normalized,
                        "status": "completed",
                    }

            except Exception as e:
                logger.error(f"Tool {tool_name} failed during search: {e}")
                yield {"type": "tool_error", "tool": tool_name, "error": str(e)}
                continue

    async def search(self, query: str, **kwargs) -> list[dict[str, Any]]:
        """
        执行搜索 (Async)

        Args:
            query: 搜索查询词
            **kwargs: 传递给工具的其他参数 (如 max_results)

        Returns:
            搜索结果列表，每个元素是一个包含 source, content 等字段的字典
        """
        aggregated_results = []
        async for event in self.search_generator(query, **kwargs):
            if event["type"] == "tool_result":
                aggregated_results.extend(event["results"])
        return aggregated_results

    def _normalize_result(self, source: str, result: Any) -> list[dict[str, Any]]:
        """将不同工具的返回结果标准化为 List[Dict]"""
        normalized = []

        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    # 确保有 source 字段
                    if "source" not in item:
                        item["source"] = source
                    normalized.append(item)
                else:
                    normalized.append({"source": source, "content": str(item)})
        elif isinstance(result, dict):
            if "source" not in result:
                result["source"] = source
            normalized.append(result)
        else:
            # String or other
            normalized.append({"source": source, "content": str(result)})

        return normalized

    async def execute(self, data: Any) -> Any:
        """
        执行搜索任务 (Agent 统一接口)

        Args:
            data: 输入数据。可以是字符串(query) 或 字典(包含 query 字段)

        Returns:
            包含 'results' 的字典
        """
        query = ""
        kwargs = {}

        if isinstance(data, str):
            query = data
        elif isinstance(data, dict):
            query = data.get("query", "")
            kwargs = data.get("kwargs", {})

        if not query:
            logger.warning("SearcherBot received empty query")
            return {"results": []}

        results = await self.search(query, **kwargs)
        return {"results": results}

    async def execute_stream(self, data: Any) -> AsyncGenerator[dict[str, Any], None]:
        """
        执行搜索任务并流式返回 (Agent 统一接口)
        """
        query = ""
        kwargs = {}

        if isinstance(data, str):
            query = data
        elif isinstance(data, dict):
            query = data.get("query", "")
            kwargs = data.get("kwargs", {})

        if not query:
            logger.warning("SearcherBot received empty query")
            yield {"type": "error", "error": "Empty query"}
            return

        async for event in self.search_generator(query, **kwargs):
            yield event
