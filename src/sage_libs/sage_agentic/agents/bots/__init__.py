"""
SAGE Agent Bots - Pre-built Agent Implementations

Layer: L3 (Core - Algorithm Library)

This module provides pre-built, ready-to-use agent bot implementations
for common tasks and workflows.

Available Bots:
- AnswerBot: Specialized in answering questions
- QuestionBot: Generates clarifying questions
- SearcherBot: Performs information retrieval
- CriticBot: Evaluates and critiques outputs
"""

from .answer_bot import AnswerBot
from .coder_bot import CoderBot
from .critic_bot import CriticBot
from .question_bot import QuestionBot
from .searcher_bot import SearcherBot

__all__ = [
    "AnswerBot",
    "CoderBot",
    "CriticBot",
    "QuestionBot",
    "SearcherBot",
]

__version__ = "0.1.0"
