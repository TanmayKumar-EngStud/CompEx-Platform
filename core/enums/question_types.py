"""
Question type enumerations for the question generation system.

This module defines all supported question types across different exam sections
and provides utilities for question type classification and handling.
"""

from enum import Enum
from typing import List, Dict, Set
from .exam_types import ExamType
from .section_types import SectionType


class QuestionType(Enum):
    """Question type classifications across all sections and exams."""
    
    # Quantitative question types
    DATA_SUFFICIENCY = "data_sufficiency"
    PROBLEM_SOLVING = "problem_solving"
    NUMERIC_ENTRY = "numeric_entry"
    QUANTITATIVE_COMPARISON = "quantitative_comparison"
    
    # Verbal question types
    READING_COMPREHENSION = "reading_comprehension"
    CRITICAL_REASONING = "critical_reasoning"
    SENTENCE_CORRECTION = "sentence_correction"
    TEXT_COMPLETION = "text_completion"
    SENTENCE_EQUIVALENCE = "sentence_equivalence"
    
    # Integrated Reasoning types (GMAT only)
    GRAPHIC_INTERPRETATION = "graphic_interpretation"
    TABLE_ANALYSIS = "table_analysis"
    TWO_PART_ANALYSIS = "two_part_analysis"
    MULTI_SOURCE_REASONING = "multi_source_reasoning"
    
    # Multiple Choice Question (general)
    MULTIPLE_CHOICE_SINGLE = "multiple_choice_single"
    MULTIPLE_CHOICE_MULTIPLE = "multiple_choice_multiple"
    
    @classmethod
    def from_string(cls, value: str) -> 'QuestionType':
        """
        Create QuestionType from string value with common abbreviations.
        
        Args:
            value: String representation of question type
            
        Returns:
            QuestionType enum value
            
        Raises:
            ValueError: If value is not a valid question type
        """
        # Handle common abbreviations and legacy formats
        abbreviations = {
            'ds': cls.DATA_SUFFICIENCY,
            'data_sufficiency': cls.DATA_SUFFICIENCY,
            'ps': cls.PROBLEM_SOLVING,
            'problem_solving': cls.PROBLEM_SOLVING,
            'ne': cls.NUMERIC_ENTRY,
            'numeric_entry': cls.NUMERIC_ENTRY,
            'qc': cls.QUANTITATIVE_COMPARISON,
            'rc': cls.READING_COMPREHENSION,
            'reading_comprehension': cls.READING_COMPREHENSION,
            'rc-s': cls.READING_COMPREHENSION,
            'rc-m': cls.READING_COMPREHENSION,
            'rc-l': cls.READING_COMPREHENSION,
            'cr': cls.CRITICAL_REASONING,
            'critical_reasoning': cls.CRITICAL_REASONING,
            'sc': cls.SENTENCE_CORRECTION,
            'sentence_correction': cls.SENTENCE_CORRECTION,
            'tc': cls.TEXT_COMPLETION,
            'text_completion': cls.TEXT_COMPLETION,
            'se': cls.SENTENCE_EQUIVALENCE,
            'sentence_equivalence': cls.SENTENCE_EQUIVALENCE,
            'gi': cls.GRAPHIC_INTERPRETATION,
            'graphic_interpretation': cls.GRAPHIC_INTERPRETATION,
            'ta': cls.TABLE_ANALYSIS,
            'table_analysis': cls.TABLE_ANALYSIS,
            'tpa': cls.TWO_PART_ANALYSIS,
            'two_part_analysis': cls.TWO_PART_ANALYSIS,
            'msr': cls.MULTI_SOURCE_REASONING,
            'multi_source_reasoning': cls.MULTI_SOURCE_REASONING,
            'mcq': cls.MULTIPLE_CHOICE_SINGLE,
            'mcq-single': cls.MULTIPLE_CHOICE_SINGLE,
            'mcq-multiple': cls.MULTIPLE_CHOICE_MULTIPLE
        }
        
        value_lower = value.lower().replace('-', '_').replace(' ', '_')
        
        if value_lower in abbreviations:
            return abbreviations[value_lower]
            
        for question_type in cls:
            if question_type.value.lower() == value_lower:
                return question_type
                
        raise ValueError(f"Invalid question type: {value}")
    
    @classmethod
    def get_section_questions(cls, section_type: SectionType, exam_type: ExamType) -> List['QuestionType']:
        """
        Get supported question types for a specific section and exam.
        
        Args:
            section_type: The section type
            exam_type: The exam type
            
        Returns:
            List of supported question types
        """
        section_question_mapping = {
            SectionType.QUANTITATIVE: {
                ExamType.GMAT: [
                    cls.DATA_SUFFICIENCY,
                    cls.PROBLEM_SOLVING
                ],
                ExamType.GRE: [
                    cls.DATA_SUFFICIENCY,
                    cls.NUMERIC_ENTRY,
                    cls.PROBLEM_SOLVING,
                    cls.QUANTITATIVE_COMPARISON
                ]
            },
            SectionType.VERBAL: {
                ExamType.GMAT: [
                    cls.READING_COMPREHENSION,
                    cls.CRITICAL_REASONING,
                    cls.SENTENCE_CORRECTION
                ],
                ExamType.GRE: [
                    cls.READING_COMPREHENSION,
                    cls.TEXT_COMPLETION,
                    cls.SENTENCE_EQUIVALENCE
                ]
            },
            SectionType.INTEGRATED_REASONING: {
                ExamType.GMAT: [
                    cls.GRAPHIC_INTERPRETATION,
                    cls.TABLE_ANALYSIS,
                    cls.TWO_PART_ANALYSIS,
                    cls.MULTI_SOURCE_REASONING
                ]
            }
        }
        
        return section_question_mapping.get(section_type, {}).get(exam_type, [])
    
    @classmethod
    def get_all_gmat_types(cls) -> List['QuestionType']:
        """Get all GMAT question types."""
        return [
            cls.DATA_SUFFICIENCY,
            cls.PROBLEM_SOLVING,
            cls.READING_COMPREHENSION,
            cls.CRITICAL_REASONING,
            cls.SENTENCE_CORRECTION,
            cls.GRAPHIC_INTERPRETATION,
            cls.TABLE_ANALYSIS,
            cls.TWO_PART_ANALYSIS,
            cls.MULTI_SOURCE_REASONING
        ]
    
    @classmethod
    def get_all_gre_types(cls) -> List['QuestionType']:
        """Get all GRE question types."""
        return [
            cls.DATA_SUFFICIENCY,
            cls.NUMERIC_ENTRY,
            cls.PROBLEM_SOLVING,
            cls.QUANTITATIVE_COMPARISON,
            cls.READING_COMPREHENSION,
            cls.TEXT_COMPLETION,
            cls.SENTENCE_EQUIVALENCE
        ]
    
    @property
    def display_name(self) -> str:
        """Human-readable question type name."""
        return self.value.replace('_', ' ').title()
    
    @property
    def short_name(self) -> str:
        """Short abbreviation for question type."""
        abbreviations = {
            self.DATA_SUFFICIENCY: "DS",
            self.PROBLEM_SOLVING: "PS",
            self.NUMERIC_ENTRY: "NE",
            self.QUANTITATIVE_COMPARISON: "QC",
            self.READING_COMPREHENSION: "RC",
            self.CRITICAL_REASONING: "CR",
            self.SENTENCE_CORRECTION: "SC",
            self.TEXT_COMPLETION: "TC",
            self.SENTENCE_EQUIVALENCE: "SE",
            self.GRAPHIC_INTERPRETATION: "GI",
            self.TABLE_ANALYSIS: "TA",
            self.TWO_PART_ANALYSIS: "TPA",
            self.MULTI_SOURCE_REASONING: "MSR",
            self.MULTIPLE_CHOICE_SINGLE: "MCQ",
            self.MULTIPLE_CHOICE_MULTIPLE: "MCQ-M"
        }
        return abbreviations.get(self, self.value.upper())
    
    @property
    def is_parent_child_type(self) -> bool:
        """Check if this question type supports parent-child structure."""
        parent_child_types = {
            self.READING_COMPREHENSION,
            self.MULTI_SOURCE_REASONING,
            self.PROBLEM_SOLVING  # Some PS questions have shared content
        }
        return self in parent_child_types
    
    @property
    def section_type(self) -> SectionType:
        """Get the section type this question belongs to."""
        section_mapping = {
            self.DATA_SUFFICIENCY: SectionType.QUANTITATIVE,
            self.PROBLEM_SOLVING: SectionType.QUANTITATIVE,
            self.NUMERIC_ENTRY: SectionType.QUANTITATIVE,
            self.QUANTITATIVE_COMPARISON: SectionType.QUANTITATIVE,
            self.READING_COMPREHENSION: SectionType.VERBAL,
            self.CRITICAL_REASONING: SectionType.VERBAL,
            self.SENTENCE_CORRECTION: SectionType.VERBAL,
            self.TEXT_COMPLETION: SectionType.VERBAL,
            self.SENTENCE_EQUIVALENCE: SectionType.VERBAL,
            self.GRAPHIC_INTERPRETATION: SectionType.INTEGRATED_REASONING,
            self.TABLE_ANALYSIS: SectionType.INTEGRATED_REASONING,
            self.TWO_PART_ANALYSIS: SectionType.INTEGRATED_REASONING,
            self.MULTI_SOURCE_REASONING: SectionType.INTEGRATED_REASONING
        }
        return section_mapping.get(self, SectionType.QUANTITATIVE)
    
    def __str__(self) -> str:
        """String representation of question type."""
        return self.value