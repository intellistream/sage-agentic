"""sage_agentic - Agent framework, planning, and workflow optimization.

PyPI: isage-agentic
Import: sage_agentic

Core modules:
- agents: Agent implementations, planners, tool selection, bots, runtime
- workflow: Workflow generation and optimization
- workflows: Concrete workflow presets
- reasoning: Search algorithms (beam, DFS, BFS, scoring)
- interface: Protocol/registry/schema definitions
- registry: Factory and registration system

Usage:
    from sage_libs.sage_agentic.agents.planning import SimpleLLMPlanner, ReActPlanner
    from sage_libs.sage_agentic.agents.runtime import Orchestrator, RuntimeConfig
    from sage_libs.sage_agentic.agents.bots import SearcherBot
"""

from sage_libs.sage_agentic._version import __author__, __email__, __version__

# Core submodules
# Interface and registry
from . import (
    agents,
    interface,
    reasoning,
    registry,
    vida,
    workflow,
    workflows,
)
from . import eval as evaluation

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
    "registry",
    "interface",
    # Async / VidaAgent core
    "vida",
]
