# SAGE Agentic Framework

**Independent package for agentic AI capabilities: tool selection, planning, workflows, and agent coordination**

[![PyPI version](https://badge.fury.io/py/isage-agentic.svg)](https://badge.fury.io/py/isage-agentic)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

`sage-agentic` provides a comprehensive framework for building agentic AI systems with:

- **Tool Selection**: Multiple strategies (keyword, embedding, hybrid, DFS-DT, Gorilla)
- **Planning Algorithms**: ReAct, Tree of Thoughts (ToT), hierarchical planning
- **Workflow Management**: Workflow orchestration and optimization
- **Agent Coordination**: Multi-agent collaboration and registry
- **SIAS**: Sample-Importance-Aware Selection for tool/trajectory curation
- **Reasoning**: Advanced reasoning capabilities and timing decisions

## 📦 Installation

```bash
# Basic installation
pip install isage-agentic

# With LLM support
pip install isage-agentic[llm]

# Development installation
pip install isage-agentic[dev]
```

## �� Quick Start

### Tool Selection

```python
from sage_agentic.agents.action.tool_selection import HybridToolSelector

# Create selector
selector = HybridToolSelector(embedder=your_embedder)

# Select tools
tools = selector.select(
    query="search for research papers",
    available_tools=all_tools,
    k=3
)
```

### Planning

```python
from sage_agentic.agents.planning import ReActPlanner

# Create planner
planner = ReActPlanner(llm=your_llm_client)

# Generate plan
plan = planner.plan(
    task="Analyze this document and summarize key findings",
    context={"document": doc_content}
)
```

### Workflow Management

```python
from sage_agentic.workflow import WorkflowEngine

# Create workflow
workflow = WorkflowEngine()

# Register and execute workflows
workflow.register("data_pipeline", pipeline_config)
result = workflow.execute("data_pipeline", inputs=data)
```

## 📚 Key Components

### 1. **Planning** (`agents/planning/`)

Planning algorithms and strategies:

- **ToT (Tree of Thoughts)**: Multi-path reasoning with backtracking
- **ReAct**: Reasoning + Acting interleaved execution
- **Hierarchical Planner**: Hierarchical task decomposition
- **Dependency Graph**: Task dependency management
- **Timing Decider**: Execution timing optimization

### 2. **Tool Selection** (`agents/action/tool_selection/`)

Tool selection strategies:

- **Keyword Selector**: Rule-based keyword matching
- **Embedding Selector**: Semantic similarity-based selection
- **Hybrid Selector**: Combined keyword + embedding approach
- **DFS-DT Selector**: Decision tree-based selection
- **Gorilla Adapter**: Gorilla-style tool retrieval

### 3. **SIAS** (`sias/`)

Sample-Importance-Aware Selection for:
- Tool selection optimization
- Trajectory curation
- Continual learning with core-set selection

### 4. **Evaluation** (`eval/`)

Agent evaluation capabilities:
- Metrics tracking
- Determinism testing
- Telemetry and monitoring

### 5. **Interfaces & Registry** (`interface/`, `interfaces/`, `registry/`)

Unified interfaces and registration system for:
- Planners
- Tool selectors
- Workflows
- Agents

## 🔧 Architecture

```
sage_agentic/
├── agents/                 # Agent implementations
│   ├── action/            # Action and tool selection
│   ├── planning/          # Planning algorithms
│   └── intent/            # Intent detection
├── workflow/              # Workflow orchestration
├── sias/                  # Sample-Importance-Aware Selection
├── reasoning/             # Reasoning capabilities
├── eval/                  # Evaluation tools
├── interface/             # Protocol definitions
├── interfaces/            # Interface implementations
└── registry/              # Component registry
```

## 🎓 Use Cases

1. **Multi-Agent Systems**: Build coordinated multi-agent workflows
2. **Tool-Augmented LLMs**: Select and use external tools intelligently
3. **Hierarchical Planning**: Decompose complex tasks into subtasks
4. **Adaptive Systems**: Use SIAS for intelligent sample selection
5. **Research**: Experiment with different planning and selection strategies

## 🔗 Integration with SAGE

This package is part of the SAGE ecosystem but can be used independently:

```python
# Standalone usage
from sage_agentic import ReActPlanner, HybridToolSelector

# With SAGE (if installed)
from sage.libs.agentic import ReActPlanner  # Compatibility layer
```

## 📖 Documentation

- **Repository**: https://github.com/intellistream/sage-agentic
- **SAGE Documentation**: https://intellistream.github.io/SAGE-Pub/
- **Issues**: https://github.com/intellistream/sage-agentic/issues

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Originally part of the [SAGE](https://github.com/intellistream/SAGE) framework, now maintained as an independent package for broader community use.

## 📧 Contact

- **Team**: IntelliStream Team
- **Email**: shuhao_zhang@hust.edu.cn
- **GitHub**: https://github.com/intellistream
