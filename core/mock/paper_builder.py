"""
Mock Paper Builder Module.

This module provides utilities for building structured mock exam papers
from generated question data. It handles the organization and formatting
of questions into proper exam paper structures.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType


@dataclass
class PaperMetadata:
    """Metadata for a mock exam paper."""
    exam_type: ExamType
    difficulty: int
    generated_at: float
    total_questions: int
    generation_time: float
    config: Dict[str, Any]


@dataclass
class SectionMetadata:
    """Metadata for an exam section."""
    section_type: SectionType
    question_count: int
    success_count: int
    error_count: int
    average_difficulty: float


class MockPaperBuilder:
    """
    Builder class for constructing mock exam papers.
    
    This class provides a fluent interface for building structured exam papers
    from generated question data, handling both GMAT and GRE formats.
    
    Example:
        >>> builder = MockPaperBuilder(ExamType.GMAT, difficulty=3)
        >>> paper = (builder
        ...     .add_section("quantitative", quant_questions)
        ...     .add_section("verbal", verbal_questions)
        ...     .add_section("integrated_reasoning", ir_questions)
        ...     .build())
    """
    
    def __init__(self, exam_type: ExamType, difficulty: int):
        """
        Initialize the paper builder.
        
        Args:
            exam_type: The exam type (GMAT or GRE)
            difficulty: Overall paper difficulty level
        """
        self.exam_type = exam_type
        self.difficulty = difficulty
        self.sections: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def add_section(
        self, 
        section_name: str, 
        question_results: List[Any],
        section_type: Optional[SectionType] = None
    ) -> 'MockPaperBuilder':
        """
        Add a section to the paper.
        
        Args:
            section_name: Name of the section
            question_results: List of question generation results
            section_type: Optional section type enum
            
        Returns:
            Self for method chaining
        """
        if section_type is None:
            section_type = self._infer_section_type(section_name)
        
        questions = []
        success_count = 0
        error_count = 0
        difficulty_sum = 0
        
        # Process question results
        for result in question_results:
            if len(result) >= 5:
                question_data = result[-1]  # Last element is the question data
                
                if isinstance(question_data, dict) and "error" not in question_data:
                    questions.append(question_data)
                    success_count += 1
                    
                    # Extract difficulty for averaging
                    if "difficulty" in question_data:
                        difficulty_sum += question_data["difficulty"]
                else:
                    error_count += 1
        
        # Calculate average difficulty
        avg_difficulty = difficulty_sum / success_count if success_count > 0 else 0
        
        # Create section metadata
        section_metadata = SectionMetadata(
            section_type=section_type,
            question_count=len(question_results),
            success_count=success_count,
            error_count=error_count,
            average_difficulty=avg_difficulty
        )
        
        # Add section to paper
        self.sections[section_name] = {
            "questions": questions,
            "metadata": section_metadata.__dict__,
            "section_type": section_type.value if section_type else section_name
        }
        
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'MockPaperBuilder':
        """
        Add custom metadata to the paper.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            Self for method chaining
        """
        self.metadata[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the final paper structure.
        
        Returns:
            Complete paper dictionary with all sections and metadata
        """
        generation_time = time.time() - self.start_time
        total_questions = sum(
            len(section["questions"]) 
            for section in self.sections.values()
        )
        
        # Create paper metadata
        paper_metadata = PaperMetadata(
            exam_type=self.exam_type,
            difficulty=self.difficulty,
            generated_at=self.start_time,
            total_questions=total_questions,
            generation_time=generation_time,
            config=self.metadata
        )
        
        # Build final paper structure
        paper = {
            "exam_type": self.exam_type.value,
            "difficulty": self.difficulty,
            "generated_at": self.start_time,
            "sections": self.sections,
            "metadata": paper_metadata.__dict__,
            "questions": self._flatten_questions(),
            "summary": self._generate_summary()
        }
        
        return paper
    
    def _infer_section_type(self, section_name: str) -> SectionType:
        """Infer section type from section name."""
        section_name_lower = section_name.lower()
        
        if "quant" in section_name_lower:
            return SectionType.QUANTITATIVE
        elif "verbal" in section_name_lower:
            return SectionType.VERBAL
        elif "integrated" in section_name_lower or "ir" in section_name_lower:
            return SectionType.INTEGRATED_REASONING
        else:
            # Default to quantitative
            return SectionType.QUANTITATIVE
    
    def _flatten_questions(self) -> List[Dict[str, Any]]:
        """Flatten all questions into a single list with section information."""
        all_questions = []
        
        for section_name, section_data in self.sections.items():
            for question in section_data["questions"]:
                question_with_section = question.copy()
                question_with_section["section"] = section_name
                question_with_section["section_type"] = section_data["section_type"]
                all_questions.append(question_with_section)
        
        return all_questions
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the paper."""
        total_questions = 0
        total_success = 0
        total_errors = 0
        section_summaries = {}
        
        for section_name, section_data in self.sections.items():
            metadata = section_data["metadata"]
            total_questions += metadata["question_count"]
            total_success += metadata["success_count"]
            total_errors += metadata["error_count"]
            
            section_summaries[section_name] = {
                "questions": metadata["success_count"],
                "errors": metadata["error_count"],
                "success_rate": metadata["success_count"] / metadata["question_count"] if metadata["question_count"] > 0 else 0,
                "average_difficulty": metadata["average_difficulty"]
            }
        
        return {
            "total_questions": total_questions,
            "successful_questions": total_success,
            "failed_questions": total_errors,
            "overall_success_rate": total_success / total_questions if total_questions > 0 else 0,
            "sections": section_summaries,
            "exam_type": self.exam_type.value,
            "difficulty_level": self.difficulty
        }