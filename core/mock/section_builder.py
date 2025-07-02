"""
Mock Section Builder Module.

This module provides utilities for building individual exam sections
with proper question organization, timing, and metadata management.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from core.enums.question_types import QuestionType


@dataclass
class QuestionInfo:
    """Information about a single question."""
    question_id: str
    question_type: QuestionType
    difficulty: int
    estimated_time: int  # in seconds
    content: Dict[str, Any]


@dataclass
class SectionConfig:
    """Configuration for a section."""
    section_type: SectionType
    exam_type: ExamType
    time_limit: int  # in minutes
    question_count: int
    difficulty_distribution: Dict[int, float]


class MockSectionBuilder:
    """
    Builder class for constructing individual exam sections.
    
    This class handles the organization of questions within sections,
    including proper ordering, timing estimates, and metadata management.
    
    Example:
        >>> builder = MockSectionBuilder(SectionType.QUANTITATIVE, ExamType.GMAT)
        >>> section = (builder
        ...     .add_question(question_data, QuestionType.DATA_SUFFICIENCY)
        ...     .add_question(question_data, QuestionType.PROBLEM_SOLVING)
        ...     .set_time_limit(75)
        ...     .build())
    """
    
    def __init__(self, section_type: SectionType, exam_type: ExamType):
        """
        Initialize the section builder.
        
        Args:
            section_type: Type of section being built
            exam_type: Exam type (GMAT or GRE)
        """
        self.section_type = section_type
        self.exam_type = exam_type
        self.questions: List[QuestionInfo] = []
        self.time_limit: Optional[int] = None
        self.metadata: Dict[str, Any] = {}
        
        # Default configurations
        self.config = self._get_default_config()
    
    def add_question(
        self, 
        question_data: Dict[str, Any], 
        question_type: QuestionType,
        estimated_time: Optional[int] = None
    ) -> 'MockSectionBuilder':
        """
        Add a question to the section.
        
        Args:
            question_data: The question content and data
            question_type: Type of question being added
            estimated_time: Estimated time to solve (in seconds)
            
        Returns:
            Self for method chaining
        """
        if estimated_time is None:
            estimated_time = self._estimate_question_time(question_type, question_data)
        
        question_info = QuestionInfo(
            question_id=question_data.get("id", f"q_{len(self.questions) + 1}"),
            question_type=question_type,
            difficulty=question_data.get("difficulty", 3),
            estimated_time=estimated_time,
            content=question_data
        )
        
        self.questions.append(question_info)
        return self
    
    def add_questions_batch(
        self, 
        questions_data: List[Tuple[Dict[str, Any], QuestionType]]
    ) -> 'MockSectionBuilder':
        """
        Add multiple questions at once.
        
        Args:
            questions_data: List of (question_data, question_type) tuples
            
        Returns:
            Self for method chaining
        """
        for question_data, question_type in questions_data:
            self.add_question(question_data, question_type)
        
        return self
    
    def set_time_limit(self, minutes: int) -> 'MockSectionBuilder':
        """
        Set the time limit for the section.
        
        Args:
            minutes: Time limit in minutes
            
        Returns:
            Self for method chaining
        """
        self.time_limit = minutes
        return self
    
    def add_section_metadata(self, key: str, value: Any) -> 'MockSectionBuilder':
        """
        Add custom metadata to the section.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            Self for method chaining
        """
        self.metadata[key] = value
        return self
    
    def shuffle_questions(self, preserve_order_for: Optional[List[QuestionType]] = None) -> 'MockSectionBuilder':
        """
        Shuffle questions while optionally preserving order for certain types.
        
        Args:
            preserve_order_for: Question types to keep in original order
            
        Returns:
            Self for method chaining
        """
        import random
        
        if preserve_order_for is None:
            preserve_order_for = []
        
        # Separate questions that should preserve order
        preserve_questions = [q for q in self.questions if q.question_type in preserve_order_for]
        shuffle_questions = [q for q in self.questions if q.question_type not in preserve_order_for]
        
        # Shuffle the non-preserved questions
        random.shuffle(shuffle_questions)
        
        # Combine back (this is a simple approach - more sophisticated ordering could be implemented)
        self.questions = shuffle_questions + preserve_questions
        
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the final section structure.
        
        Returns:
            Complete section dictionary with questions and metadata
        """
        # Calculate section statistics
        total_estimated_time = sum(q.estimated_time for q in self.questions)
        difficulty_counts = {}
        question_type_counts = {}
        
        for question in self.questions:
            # Count difficulties
            difficulty = question.difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            
            # Count question types
            qtype = question.question_type.value
            question_type_counts[qtype] = question_type_counts.get(qtype, 0) + 1
        
        # Build section structure
        section = {
            "section_type": self.section_type.value,
            "exam_type": self.exam_type.value,
            "time_limit_minutes": self.time_limit or self.config.time_limit,
            "question_count": len(self.questions),
            "questions": [self._format_question(q) for q in self.questions],
            "metadata": {
                "total_estimated_time_seconds": total_estimated_time,
                "average_estimated_time_seconds": total_estimated_time / len(self.questions) if self.questions else 0,
                "difficulty_distribution": difficulty_counts,
                "question_type_distribution": question_type_counts,
                "average_difficulty": sum(q.difficulty for q in self.questions) / len(self.questions) if self.questions else 0,
                **self.metadata
            },
            "config": self.config.__dict__ if hasattr(self.config, '__dict__') else {},
            "generated_at": time.time()
        }
        
        return section
    
    def _get_default_config(self) -> SectionConfig:
        """Get default configuration for the section type and exam type."""
        if self.exam_type == ExamType.GMAT:
            if self.section_type == SectionType.QUANTITATIVE:
                return SectionConfig(
                    section_type=self.section_type,
                    exam_type=self.exam_type,
                    time_limit=75,
                    question_count=31,
                    difficulty_distribution={1: 0.1, 2: 0.2, 3: 0.4, 4: 0.2, 5: 0.1}
                )
            elif self.section_type == SectionType.VERBAL:
                return SectionConfig(
                    section_type=self.section_type,
                    exam_type=self.exam_type,
                    time_limit=75,
                    question_count=36,
                    difficulty_distribution={1: 0.1, 2: 0.2, 3: 0.4, 4: 0.2, 5: 0.1}
                )
            elif self.section_type == SectionType.INTEGRATED_REASONING:
                return SectionConfig(
                    section_type=self.section_type,
                    exam_type=self.exam_type,
                    time_limit=30,
                    question_count=12,
                    difficulty_distribution={1: 0.1, 2: 0.2, 3: 0.4, 4: 0.2, 5: 0.1}
                )
        
        elif self.exam_type == ExamType.GRE:
            if self.section_type == SectionType.QUANTITATIVE:
                return SectionConfig(
                    section_type=self.section_type,
                    exam_type=self.exam_type,
                    time_limit=35,
                    question_count=20,
                    difficulty_distribution={1: 0.15, 2: 0.25, 3: 0.3, 4: 0.2, 5: 0.1}
                )
            elif self.section_type == SectionType.VERBAL:
                return SectionConfig(
                    section_type=self.section_type,
                    exam_type=self.exam_type,
                    time_limit=30,
                    question_count=20,
                    difficulty_distribution={1: 0.15, 2: 0.25, 3: 0.3, 4: 0.2, 5: 0.1}
                )
        
        # Default fallback
        return SectionConfig(
            section_type=self.section_type,
            exam_type=self.exam_type,
            time_limit=60,
            question_count=20,
            difficulty_distribution={1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2}
        )
    
    def _estimate_question_time(self, question_type: QuestionType, question_data: Dict[str, Any]) -> int:
        """
        Estimate time to solve a question based on type and content.
        
        Args:
            question_type: Type of question
            question_data: Question content and data
            
        Returns:
            Estimated time in seconds
        """
        # Base times by question type (in seconds)
        base_times = {
            QuestionType.DATA_SUFFICIENCY: 120,
            QuestionType.PROBLEM_SOLVING: 120,
            QuestionType.READING_COMPREHENSION: 180,
            QuestionType.CRITICAL_REASONING: 120,
            QuestionType.SENTENCE_CORRECTION: 90,
            QuestionType.TEXT_COMPLETION: 90,
            QuestionType.SENTENCE_EQUIVALENCE: 90,
            QuestionType.NUMERIC_ENTRY: 120,
            QuestionType.GRAPHIC_INTERPRETATION: 150,
            QuestionType.TABLE_ANALYSIS: 150,
            QuestionType.TWO_PART_ANALYSIS: 180,
            QuestionType.MULTI_SOURCE_REASONING: 180
        }
        
        base_time = base_times.get(question_type, 120)
        
        # Adjust for difficulty
        difficulty = question_data.get("difficulty", 3)
        difficulty_multiplier = 0.7 + (difficulty - 1) * 0.15  # 0.7 to 1.3
        
        # Adjust for content complexity (rough heuristic)
        content_length = len(str(question_data.get("content", "")))
        if content_length > 1000:
            complexity_multiplier = 1.2
        elif content_length > 500:
            complexity_multiplier = 1.1
        else:
            complexity_multiplier = 1.0
        
        estimated_time = int(base_time * difficulty_multiplier * complexity_multiplier)
        
        return estimated_time
    
    def _format_question(self, question_info: QuestionInfo) -> Dict[str, Any]:
        """Format a question for inclusion in the section."""
        formatted = question_info.content.copy()
        formatted.update({
            "question_id": question_info.question_id,
            "question_type": question_info.question_type.value,
            "estimated_time_seconds": question_info.estimated_time,
            "section_type": self.section_type.value
        })
        
        return formatted