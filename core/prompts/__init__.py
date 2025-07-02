"""
Core Prompt Generation Module.

This module provides unified prompt generation functionality for both GMAT and GRE exams.
It implements a factory pattern to create exam and section-specific prompt generators.

Classes:
    PromptGeneratorFactory: Factory for creating prompt generators
    BasePromptGenerator: Abstract base for all prompt generators
    
Example:
    >>> from core.prompts import PromptGeneratorFactory
    >>> from core.enums import ExamType, SectionType
    >>> factory = PromptGeneratorFactory()
    >>> generator = factory.create_prompt_generator(
    ...     exam_type=ExamType.GMAT,
    ...     section_type=SectionType.QUANTITATIVE,
    ...     difficulty=3
    ... )
    >>> prompts = generator.generate_question_prompts()
"""

from .prompt_generator_factory import PromptGeneratorFactory
from .base.base_prompt_generator import BasePromptGenerator

__all__ = [
    'PromptGeneratorFactory',
    'BasePromptGenerator'
]