"""sage_agentic - Agent framework, planning, and workflow optimization.

PyPI: isage-agentic
Import: sage_agentic

Core modules:
- agents: Agent implementations, planners, tool selection, bots, runtime
- workflow: Workflow generation and optimization
- workflows: Concrete workflow presets
- reasoning: Search algorithms (beam, DFS, BFS, scoring)
- interfaces: Protocol definitions
- registry: Factory and registration system

Usage:
    from sage_libs.sage_agentic.agents.planning import SimpleLLMPlanner, ReActPlanner
    from sage_libs.sage_agentic.agents.runtime import Orchestrator, RuntimeConfig
    from sage_libs.sage_agentic.agents.bots import SearcherBot
"""

__version__ = "0.1.0.0"
__author__ = "IntelliStream Team"
__email__ = "shuhao_zhang@hust.edu.cn"

# Core submodules
from . import (
    agents,
    reasoning,
    workflow,
    workflows,
)
from . import eval as evaluation

# Interface and registry
from . import interface, interfaces, registry

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    # Core modules
    "agents",
    "workflow",
    "workflows",
    "reasoning",
    "evaluation",
    # Interface layer
    "interfaces",
    "registry",
    "interface",
]
