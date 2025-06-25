"""
Section type enumerations for the question generation system.

This module defines the different sections within exams and provides
utilities for section-specific handling.
"""

from enum import Enum
from typing import List, Dict
from .exam_types import ExamType


class SectionType(Enum):
    """Examination section types."""
    
    QUANTITATIVE = "quantitative"
    VERBAL = "verbal"
    INTEGRATED_REASONING = "integrated_reasoning"
    
    @classmethod
    def from_string(cls, value: str) -> 'SectionType':
        """
        Create SectionType from string value.
        
        Args:
            value: String representation of section type
            
        Returns:
            SectionType enum value
            
        Raises:
            ValueError: If value is not a valid section type
        """
        # Handle common abbreviations
        abbreviations = {
            'quants': cls.QUANTITATIVE,
            'q': cls.QUANTITATIVE,
            'verbal': cls.VERBAL,
            'v': cls.VERBAL,
            'ir': cls.INTEGRATED_REASONING,
            'integrated': cls.INTEGRATED_REASONING
        }
        
        value_lower = value.lower().replace('_', '').replace('-', '')
        
        if value_lower in abbreviations:
            return abbreviations[value_lower]
            
        for section_type in cls:
            if section_type.value.lower().replace('_', '') == value_lower:
                return section_type
                
        raise ValueError(f"Invalid section type: {value}")
    
    @classmethod
    def get_supported_sections(cls, exam_type: ExamType) -> List['SectionType']:
        """
        Get supported sections for a specific exam type.
        
        Args:
            exam_type: The exam type to get sections for
            
        Returns:
            List of supported section types
        """
        section_mapping = {
            ExamType.GMAT: [
                cls.QUANTITATIVE,
                cls.VERBAL,
                cls.INTEGRATED_REASONING
            ],
            ExamType.GRE: [
                cls.QUANTITATIVE,
                cls.VERBAL
            ]
        }
        
        return section_mapping.get(exam_type, [])
    
    @property
    def display_name(self) -> str:
        """Human-readable section name."""
        return self.value.replace('_', ' ').title()
    
    @property
    def short_name(self) -> str:
        """Short abbreviation for section."""
        abbreviations = {
            self.QUANTITATIVE: "Quants",
            self.VERBAL: "Verbal", 
            self.INTEGRATED_REASONING: "IR"
        }
        return abbreviations.get(self, self.value)
    
    def __str__(self) -> str:
        """String representation of section type."""
        return self.value