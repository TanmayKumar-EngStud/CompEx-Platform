"""
Base Exam Configuration Module.

This module provides the abstract base class for exam-specific configurations,
defining the common interface and shared functionality for all exam types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType


@dataclass
class BaseExamConfig(ABC):
    """
    Abstract base class for exam configurations.
    
    This class defines the common interface for all exam-specific configurations,
    providing a standard way to access exam parameters and requirements.
    
    Attributes:
        exam_type: The exam type (GMAT or GRE)
        difficulty: Overall exam difficulty level (1-5)
        sections: List of sections for this exam
        max_workers: Maximum number of worker threads for generation
        api_instances: Number of API instances to use
        requests_per_instance: Requests per API instance in time window
        time_window: Time window for rate limiting (seconds)
    """
    
    exam_type: ExamType
    difficulty: int
    sections: List[SectionType]
    max_workers: int = 10
    api_instances: int = 5
    requests_per_instance: int = 60
    time_window: int = 60
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (1 <= self.difficulty <= 5):
            raise ValueError("Difficulty must be between 1 and 5")
        
        if self.max_workers < 1:
            raise ValueError("Max workers must be at least 1")
        
        if self.api_instances < 1:
            raise ValueError("API instances must be at least 1")
        
        if not self.sections:
            raise ValueError("Must have at least one section")
    
    @abstractmethod
    def get_section_config(self, section_type: SectionType) -> Dict[str, Any]:
        """
        Get configuration for a specific section.
        
        Args:
            section_type: The section type to get config for
            
        Returns:
            Dictionary containing section-specific configuration
        """
        pass
    
    @abstractmethod
    def get_question_distribution(self, section_type: SectionType) -> Dict[str, int]:
        """
        Get question distribution for a section.
        
        Args:
            section_type: The section type
            
        Returns:
            Dictionary mapping question types to counts
        """
        pass
    
    @abstractmethod
    def get_total_questions(self) -> int:
        """
        Get total number of questions for the entire exam.
        
        Returns:
            Total question count
        """
        pass
    
    @abstractmethod
    def get_time_limits(self) -> Dict[SectionType, int]:
        """
        Get time limits for each section in minutes.
        
        Returns:
            Dictionary mapping section types to time limits
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_difficulty(cls, difficulty: int) -> 'BaseExamConfig':
        """
        Create configuration from difficulty level.
        
        Args:
            difficulty: Difficulty level (1-5)
            
        Returns:
            Configured exam instance
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "exam_type": self.exam_type.value,
            "difficulty": self.difficulty,
            "sections": [section.value for section in self.sections],
            "max_workers": self.max_workers,
            "api_instances": self.api_instances,
            "requests_per_instance": self.requests_per_instance,
            "time_window": self.time_window,
            "section_configs": {
                section.value: self.get_section_config(section)
                for section in self.sections
            },
            "question_distributions": {
                section.value: self.get_question_distribution(section)
                for section in self.sections
            },
            "time_limits": {
                section.value: limit
                for section, limit in self.get_time_limits().items()
            },
            "total_questions": self.get_total_questions()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseExamConfig':
        """
        Create configuration from dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            Configured exam instance
        """
        exam_type = ExamType(data["exam_type"])
        difficulty = data["difficulty"]
        
        # Create appropriate subclass instance
        if exam_type == ExamType.GMAT:
            from .gmat_config import GMATConfig
            return GMATConfig.from_difficulty(difficulty)
        elif exam_type == ExamType.GRE:
            from .gre_config import GREConfig
            return GREConfig.from_difficulty(difficulty)
        else:
            raise ValueError(f"Unknown exam type: {exam_type}")
    
    def validate_section_type(self, section_type: SectionType) -> bool:
        """
        Validate that a section type is supported by this exam.
        
        Args:
            section_type: Section type to validate
            
        Returns:
            True if section is supported, False otherwise
        """
        return section_type in self.sections
    
    def get_section_weight(self, section_type: SectionType) -> float:
        """
        Get the weight/importance of a section in the overall exam.
        
        Args:
            section_type: Section type
            
        Returns:
            Weight as a float between 0 and 1
        """
        # Default equal weighting
        return 1.0 / len(self.sections)
    
    def get_difficulty_distribution(self, section_type: SectionType) -> Dict[int, float]:
        """
        Get difficulty distribution for a section based on overall exam difficulty.
        
        Args:
            section_type: Section type
            
        Returns:
            Dictionary mapping difficulty levels (1-5) to probabilities
        """
        # Base distribution templates
        distributions = {
            1: {1: 0.7, 2: 0.2, 3: 0.1, 4: 0.0, 5: 0.0},
            2: {1: 0.5, 2: 0.3, 3: 0.15, 4: 0.05, 5: 0.0},
            3: {1: 0.2, 2: 0.3, 3: 0.3, 4: 0.15, 5: 0.05},
            4: {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.3, 5: 0.1},
            5: {1: 0.0, 2: 0.1, 3: 0.2, 4: 0.4, 5: 0.3}
        }
        
        return distributions.get(self.difficulty, distributions[3])