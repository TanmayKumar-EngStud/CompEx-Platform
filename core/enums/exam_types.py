"""
Exam type enumerations for the question generation system.

This module defines the supported examination types and provides utilities
for type-safe exam type handling throughout the system.
"""

from enum import Enum
from typing import List


class ExamType(Enum):
    """Supported examination types."""
    
    GMAT = "gmat"
    GRE = "gre"
    
    @classmethod
    def from_string(cls, value: str) -> 'ExamType':
        """
        Create ExamType from string value.
        
        Args:
            value: String representation of exam type
            
        Returns:
            ExamType enum value
            
        Raises:
            ValueError: If value is not a valid exam type
        """
        for exam_type in cls:
            if exam_type.value.lower() == value.lower():
                return exam_type
        raise ValueError(f"Invalid exam type: {value}")
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all exam type values as strings."""
        return [exam_type.value for exam_type in cls]
    
    @property
    def display_name(self) -> str:
        """Human-readable exam type name."""
        return self.value.upper()
    
    def __str__(self) -> str:
        """String representation of exam type."""
        return self.value