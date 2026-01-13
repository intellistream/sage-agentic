# SAGE Agentic (isage-agentic) - Copilot Instructions

## Package Identity

| 属性 | 值 |
|-----|-----|
| **PyPI 包名** | `isage-agentic` |
| **导入名称** | `sage_libs.sage_agentic` |
| **SAGE 架构层级** | **L3 (Algorithm Library)** |
| **版本格式** | 四段式 `0.0.0.x` |
| **仓库** | `intellistream/sage-agentic` |

## 层级定位

这是一个 **L3 纯算法库**，提供 Agent 框架的具体实现。

### ✅ 允许的依赖

- Python 标准库
- `sage-common` (L1) - 通过 SAGE 框架使用时
- `sage-libs` 接口层 (L3) - 注册到 SAGE 工厂
- 轻量级第三方库

### ❌ 禁止的依赖

- 任何 L4+ 层的包 (`sage-middleware`, `sage-kernel`)
- 向量数据库、内存系统（属于 middleware）
- 网络服务、数据库连接
- 重型运行时后端

## 与 SAGE 主仓库的关系

### SAGE 侧 (`sage.libs.agentic`)

SAGE 主仓库中的 `sage.libs.agentic` 包含：

1. **接口层** (`sage.libs.agentic.interface`)：
   - 抽象基类：`Agent`, `Tool`, `Planner`, `ReflectionEngine`
   - 工厂函数：`create_agent()`, `create_planner()`, `register_agent()` 等

2. **类型定义**：
   - `AgentState`, `AgentAction`, `ToolResult`
   - 规划相关类型

### 本包 (`sage_libs.sage_agentic`) 提供

**具体实现**，通过 `_register.py` 自动注册到 SAGE 工厂：

- `ReActAgent` - ReAct 范式 Agent
- `PlanExecuteAgent` - 先规划后执行 Agent
- `ReflexAgent` - 反思型 Agent
- `SequentialPlanner`, `TreeOfThoughtPlanner` - 规划器实现
- 内置工具集

## 导入方式

```python
# 方式 1：直接使用（独立模式）
from sage_libs.sage_agentic import ReActAgent, PlanExecuteAgent

# 方式 2：通过 SAGE 工厂（集成模式）
import sage_libs.sage_agentic  # 触发自动注册
from sage.libs.agentic import create_agent
agent = create_agent("react")
```

## 目录结构

```
sage-agentic/
├── src/
│   └── sage_libs/
│       ├── __init__.py          # namespace package (pkgutil.extend_path)
│       └── sage_agentic/
│           ├── __init__.py      # 主入口，定义 __version__
│           ├── agents/
│           ├── workflow/
│           ├── workflows/
│           ├── reasoning/
│           ├── interfaces/ 与 interface/
│           └── registry/
├── tests/
├── pyproject.toml
└── README.md
```

## 重要说明

### 关于 SAGE 中间件中的 Agent Operators

SAGE `sage-middleware` 中有 Agent 相关的 **算子 (Operators)**：
- `sage.middleware.operators.agentic.runtime`
- `sage.middleware.operators.agentic.planning_operator`
- `sage.middleware.operators.agentic.tool_selection_operator`

这些是**中间件算子**，它们：
1. 可以使用本包 (`sage_agentic`) 的实现
2. 可以访问向量数据库、内存系统等 L4 资源
3. 是 SAGE dataflow 的一部分

**本包只提供纯算法实现**，不依赖任何 middleware 资源。

## 常见问题修复指南

### 问题 1：循环依赖

**错误**：本包不应导入 `sage.middleware.*`

**检查**：
```python
# ❌ 错误
from sage.middleware.operators.agentic import xxx

# ✅ 正确
from sage.libs.agentic import xxx  # 只能导入接口层
```

### 问题 2：导入路径错误

**检查**：
1. 确认 `pyproject.toml` 中使用 src layout (`package-dir = {"" = "src"}`) 且 find 包含 `sage_libs*`
2. 确认 `src/sage_libs/sage_agentic/__init__.py` 导出正确

### 问题 3：与 SAGE middleware 的区别

| 组件 | 位置 | 用途 |
|-----|------|------|
| `sage_libs.sage_agentic.ReActAgent` | 本包 | 纯算法实现 |
| `sage.middleware.operators.agentic.runtime` | SAGE middleware | Dataflow 算子，可访问 VDB/Memory |

## 测试

```bash
# 运行测试
pytest tests/ -v

# 独立模式测试
pytest tests/ -v -k "not integration"
```

## 发布（标准：isage-pypi-publisher）

1. 清理旧构建：`rm -rf dist build *.egg-info src/isage_agentic.egg-info`
2. 构建发行物：`python -m build`
3. 发布到 TestPyPI 验证：`isage-pypi-publisher --repository testpypi dist/*`
4. 发布到 PyPI：`isage-pypi-publisher dist/*`
5. 版本递增：同步更新 `pyproject.toml` 与 `src/sage_libs/sage_agentic/__init__.py` 的版本号（breaking change 用次/主版本）
