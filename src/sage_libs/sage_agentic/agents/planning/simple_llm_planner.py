# sage/libs/agentic/agents/planning/llm_planner.py
from __future__ import annotations

import json
import logging
import re
from typing import Any

from .utils.repair import extract_json_array

logger = logging.getLogger(__name__)

PlanStep = dict[
    str, Any
]  # MCP风格：{"type":"tool","name":"...","arguments":{...}} | {"type":"reply","text":"..."}


def _top_k_tools(
    user_query: str, tools: dict[str, dict[str, Any]], k: int = 6
) -> dict[str, dict[str, Any]]:
    """基于 name/description 的匹配."""
    uq = user_query.lower()
    scored: list[tuple[str, float]] = []
    for name, meta in tools.items():
        txt = (name + " " + str(meta.get("description", ""))).lower()
        score = 0.0
        for token in re.findall(r"[a-zA-Z0-9_]+", uq):
            if token in txt:
                score += 1.0
        if name.lower() in uq:
            score += 1.5
        scored.append((name, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    keep = [n for n, s in scored[:k] if s > 0] or list(tools.keys())[: min(k, len(tools))]
    return {n: tools[n] for n in keep}


def _build_prompt(
    profile_system_prompt: str, user_query: str, tools_subset: dict[str, dict[str, Any]]
) -> str:
    """
    把 Profile + 用户问题 + 工具清单 拼成一个强约束提示词，只允许输出 JSON。
    工具清单需包含 MCP 三要素：name/description/input_schema
    """
    tool_list = [
        {
            "name": name,
            "description": meta.get("description", ""),
            "input_schema": meta.get("input_schema", {}),
        }
        for name, meta in tools_subset.items()
    ]
    # 只输出 JSON，且必须是数组
    return f"""<SYSTEM>
You are a planning module. Produce a plan as a JSON array of steps.
Each step is EITHER:
  1) A tool call: {{"type":"tool","name":"<tool_name>","arguments":{{...}}}}
  2) A final reply: {{"type":"reply","text":"..."}}

Rules:
- Always call at least one tool before replying when tools are provided.
- Use ONLY the provided tools (names & schemas below).
- Arguments MUST follow the JSON Schema of the selected tool.
- Return ONLY the JSON array. Do NOT include extra text, code fences, or explanations.
- Keep steps concise. Conclude with a reply step once done.

</SYSTEM>

<PROFILE>
{profile_system_prompt}
</PROFILE>

<USER_QUERY>
{user_query}
</USER_QUERY>

<AVAILABLE_TOOLS>
{json.dumps(tool_list, ensure_ascii=False)}
</AVAILABLE_TOOLS>

Output: JSON array only.
"""


def _validate_steps(
    steps: list[dict[str, Any]], tools: dict[str, dict[str, Any]]
) -> list[PlanStep]:
    """
    轻量校验：结构正确性 + 工具是否存在 + 必填参数是否齐全（基于 schema.required）。
    不通过时，直接过滤掉错误步；
    """
    valid: list[PlanStep] = []
    for step in steps:
        if not isinstance(step, dict) or "type" not in step:
            continue

        if step["type"] == "reply":
            if isinstance(step.get("text"), str) and step["text"].strip():
                valid.append({"type": "reply", "text": step["text"].strip()})
            continue

        if step["type"] == "tool":
            name = step.get("name")
            args = step.get("arguments", {})
            if not isinstance(name, str) or name not in tools or not isinstance(args, dict):
                continue

            # 基于 MCP input_schema 的必填项检查
            schema = tools[name].get("input_schema") or {}
            req = schema.get("required") or []
            if all(k in args for k in req):
                valid.append({"type": "tool", "name": name, "arguments": args})
            # 若缺少必填参数，丢弃该步（可扩展为“补齐参数”的对话步骤）
            continue
    # 保底：没有可执行步时，加一个 reply
    if not valid:
        valid = [{"type": "reply", "text": "（计划不可用）"}]
    return valid


class SimpleLLMPlanner:
    """
    用.rag.generator 中的 Generator（OpenAIGenerator / HFGenerator）产出 MCP 风格计划。
    统一接口：plan(profile_prompt, user_query, tools) -> List[PlanStep]
    """

    def __init__(
        self,
        generator,
        max_steps: int = 6,
        enable_repair: bool = True,
        topk_tools: int = 6,
    ):
        """
        :param generator: 你的 OpenAIGenerator 或 HFGenerator 实例（具备 .execute([user_query, prompt])）
        :param max_steps: 返回的最大步骤数
        :param enable_repair: 当 JSON 解析失败时，是否自动修复一次
        :param topk_tools: 传给模型的工具子集大小（减小提示长度与跑偏率）
        """
        self.generator = generator
        self.max_steps = max_steps
        self.enable_repair = enable_repair
        self.topk_tools = topk_tools

    def _ask_llm(self, prompt: str, user_query: str) -> str:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query},
        ]
        _, out = self.generator.execute([user_query, messages])
        return out

    def plan_stream(
        self,
        profile_system_prompt: str,
        user_query: str,
        tools: dict[str, dict[str, Any]],
    ):
        """
        流式规划接口，Yield 规划过程中的思考和最终计划
        """
        # 1) 缩小工具集合，减少上下文
        yield {"type": "thought", "content": "正在筛选相关工具..."}
        tools_subset = _top_k_tools(user_query, tools, k=self.topk_tools)
        yield {
            "type": "thought",
            "content": f"已选定 {len(tools_subset)} 个工具: {', '.join(tools_subset.keys())}",
        }

        # 2) 首次请求
        yield {"type": "thought", "content": "正在生成执行计划..."}
        prompt = _build_prompt(profile_system_prompt, user_query, tools_subset)
        out = self._ask_llm(prompt, user_query)
        steps = extract_json_array(out)

        # 调试信息：记录原始输出
        if steps is None:
            logger.debug(f"🐛 Debug: 无法解析计划 JSON。原始输出:\n{out[:500]}...")
            yield {"type": "thought", "content": "计划解析失败，尝试自动修复..."}

        # 3) 自动修复（仅一次）
        if steps is None and self.enable_repair:
            repair_prompt = (
                "Your output was invalid. Return ONLY a JSON array of steps. No prose, no fences.\n"
                'Example: [{"type":"tool","name":"...","arguments":{...}}, {"type":"reply","text":"..."}]'
            )
            _, out2 = self.generator.execute(
                [user_query, repair_prompt + "\n\nPrevious output:\n" + out]
            )
            steps = extract_json_array(out2)

            # 调试信息：记录修复后的输出
            if steps is None:
                logger.debug(f"🐛 Debug: 修复后仍无法解析 JSON。修复输出:\n{out2[:500]}...")
                yield {"type": "thought", "content": "自动修复失败，将直接回复。"}

        # 4) 兜底：若仍无法解析，直接把原文作为 reply
        if steps is None:
            logger.debug("🐛 Debug: 使用兜底策略，返回原文作为回复")
            final_steps = [{"type": "reply", "text": out.strip()[:2000]}][: self.max_steps]
            yield {"type": "plan", "steps": final_steps}
            return

        # 5) 轻量合法化（结构+必填参数）
        steps = _validate_steps(steps, tools_subset)

        # 6) 截断并返回
        final_steps = steps[: self.max_steps]
        yield {"type": "plan", "steps": final_steps}

    def plan(
        self,
        profile_system_prompt: str,
        user_query: str,
        tools: dict[str, dict[str, Any]],
    ) -> list[PlanStep]:
        # 非流式入口：收集流式结果并返回最终计划
        final_plan = []
        for event in self.plan_stream(profile_system_prompt, user_query, tools):
            if event["type"] == "plan":
                final_plan = event["steps"]
        return final_plan

    def _tools_to_manifest(self, tools_like: Any) -> dict[str, dict[str, Any]]:
        """
        支持：
        - 直接传工具清单 dict[str, {description,input_schema}]
        - 传 MCPRegistry 实例（具备 .describe()）
        """
        if isinstance(tools_like, dict):
            return tools_like
        if hasattr(tools_like, "describe") and callable(tools_like.describe):
            result = tools_like.describe()
            # Type assertion: describe() should return a dict of tool manifests
            if not isinstance(result, dict):
                raise TypeError(f"Expected describe() to return dict, got {type(result).__name__}")
            return result
        raise TypeError(
            "SimplePlanner expects `tools` as a dict manifest or an object with .describe()."
        )

    def execute(self, data: Any) -> list[PlanStep]:
        """
        统一入口，支持以下输入形态（任选其一）：
        1) dict：
           {
             "profile_prompt" | "profile_system_prompt": str,
             "user_query" | "query": str,
             "tools" | "registry": dict 或 具备 .describe() 的对象,
             # 可选： "topk": int    # 仅本次调用的临时 top-k 覆写
           }

        2) 三元组：(profile_prompt: str, user_query: str, tools_or_registry)

        返回：List[PlanStep]
        """
        # --- 形态 1：dict ---
        if isinstance(data, dict):
            profile_prompt = data.get("profile_prompt") or data.get("profile_system_prompt")
            user_query = data.get("user_query") or data.get("query")
            tools_like = data.get("tools") or data.get("registry")
            if (
                not isinstance(profile_prompt, str)
                or not isinstance(user_query, str)
                or tools_like is None
            ):
                raise ValueError(
                    "SimplePlanner.execute(dict) requires 'profile_prompt' (or 'profile_system_prompt'), "
                    "'user_query' (or 'query'), and 'tools' (or 'registry')."
                )

            # 临时 top-k 覆写（不修改实例字段）
            original_topk = self.topk_tools
            if "topk" in data:
                if not isinstance(data["topk"], int) or data["topk"] <= 0:
                    raise ValueError("'topk' must be a positive int.")
                self.topk_tools = data["topk"]

            try:
                tools_manifest = self._tools_to_manifest(tools_like)
                return self.plan(profile_prompt, user_query, tools_manifest)
            finally:
                # 还原
                self.topk_tools = original_topk

        # --- 形态 2：三元组 ---
        if isinstance(data, tuple) and len(data) == 3:
            profile_prompt, user_query, tools_like = data
            if not isinstance(profile_prompt, str) or not isinstance(user_query, str):
                raise TypeError("Tuple form must be (str, str, tools_or_registry).")
            tools_manifest = self._tools_to_manifest(tools_like)
            return self.plan(profile_prompt, user_query, tools_manifest)

        raise TypeError(
            "SimplePlanner.execute expects either a dict with keys "
            "('profile_prompt'/'profile_system_prompt', 'user_query'/'query', 'tools'/'registry') "
            "or a tuple (profile_prompt, user_query, tools_or_registry)."
        )
