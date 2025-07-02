"""
Core Mock Generation Module.

This module provides unified mock generation functionality for both GMAT and GRE exams.
It implements a strategy pattern to handle exam-specific differences while maintaining
a common interface and shared logic.

Classes:
    UnifiedMockGenerator: Main unified mock generator class
    MockPaperBuilder: Builder for creating mock papers
    MockSectionBuilder: Builder for creating individual sections
    
Example:
    >>> from core.mock import UnifiedMockGenerator
    >>> from core.enums import ExamType
    >>> generator = UnifiedMockGenerator(ExamType.GMAT, difficulty=3)
    >>> paper = generator.generate_mock_paper()
"""

from .unified_mock_generator import UnifiedMockGenerator
from .paper_builder import MockPaperBuilder
from .section_builder import MockSectionBuilder

__all__ = [
    'UnifiedMockGenerator',
    'MockPaperBuilder', 
    'MockSectionBuilder'
]