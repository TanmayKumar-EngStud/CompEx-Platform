"""
Template classes for question generation components.

This module provides a clean, class-based interface for loading and managing
question generation templates, replacing the complex pattern matching system
in BaseQuestionComponent.
"""

from .question_metadata import QuestionMetadata
from .question_text import QuestionText
from .question_title import QuestionTitle
from .question_solution import QuestionSolution
from .question_options import QuestionOptions
from .question_answer import QuestionAnswer

__all__ = [
    'QuestionMetadata',
    'QuestionText', 
    'QuestionTitle',
    'QuestionSolution',
    'QuestionOptions',
    'QuestionAnswer'
]