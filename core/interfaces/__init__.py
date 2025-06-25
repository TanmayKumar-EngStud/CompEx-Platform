"""
Interfaces module for abstract base classes and protocols.

This module defines the contracts that different components must implement,
enabling consistent behavior across exam types and question generators.
"""

from .question_generator import IQuestionGenerator
from .mock_generator import IMockGenerator
from .prompt_generator import IPromptGenerator

__all__ = [
    "IQuestionGenerator",
    "IMockGenerator", 
    "IPromptGenerator"
]