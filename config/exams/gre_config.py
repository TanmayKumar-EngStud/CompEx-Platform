"""
GRE Exam Configuration Module.

This module provides GRE-specific configuration including section requirements,
question distributions, and timing parameters.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from .base_exam_config import BaseExamConfig


@dataclass 
class GREConfig(BaseExamConfig):
    """
    GRE-specific exam configuration.
    
    Defines the structure, requirements, and parameters for GRE exams including
    the two main sections: Quantitative and Verbal (each appearing twice).
    
    Attributes:
        quant_sections: Number of quantitative sections (typically 2)
        verbal_sections: Number of verbal sections (typically 2)
        questions_per_quant_section: Questions per quantitative section
        questions_per_verbal_section: Questions per verbal section
    """
    
    quant_sections: int = 2
    verbal_sections: int = 2
    questions_per_quant_section: int = 15
    questions_per_verbal_section: int = 15
    
    def __post_init__(self):
        """Initialize GRE-specific configuration."""
        # Set GRE-specific defaults
        self.exam_type = ExamType.GRE
        
        # Define GRE sections (always Quantitative and Verbal)
        self.sections = [
            SectionType.QUANTITATIVE,
            SectionType.VERBAL
        ]
        
        # Call parent validation
        super().__post_init__()
    
    @classmethod
    def from_difficulty(cls, difficulty: int) -> 'GREConfig':
        """
        Create GRE configuration from difficulty level.
        
        Args:
            difficulty: Difficulty level (1-5)
            
        Returns:
            Configured GRE instance
        """
        return cls(
            exam_type=ExamType.GRE,
            difficulty=difficulty,
            sections=[],  # Will be set in __post_init__
            max_workers=10,
            api_instances=5,
            requests_per_instance=60,
            time_window=60,
            quant_sections=2,
            verbal_sections=2,
            questions_per_quant_section=15,
            questions_per_verbal_section=15
        )
    
    def get_section_config(self, section_type: SectionType) -> Dict[str, Any]:
        """Get GRE section-specific configuration."""
        configs = {
            SectionType.QUANTITATIVE: {
                "question_count": self.questions_per_quant_section,
                "sections": self.quant_sections,
                "time_limit_minutes": 35,
                "question_types": ["PS", "QC", "NE", "PC"],  # Problem Solving, Quantitative Comparison, Numeric Entry, Parent-Child
                "topics": ["arithmetic", "algebra", "geometry", "data_analysis"],
                "question_distribution": {
                    "PS": 8,   # Problem Solving (most common)
                    "QC": 3,   # Quantitative Comparison
                    "NE": 2,   # Numeric Entry
                    "PC": 2    # Parent-Child (shared data)
                }
            },
            SectionType.VERBAL: {
                "question_count": self.questions_per_verbal_section,
                "sections": self.verbal_sections,
                "time_limit_minutes": 30,
                "question_types": ["RC", "TC", "SE"],  # Reading Comprehension, Text Completion, Sentence Equivalence
                "question_distribution": {
                    "RC": 4,   # Reading Comprehension
                    "TC": 6,   # Text Completion
                    "SE": 5    # Sentence Equivalence
                },
                "rc_passage_types": ["rc-s", "rc-m", "rc-l"],  # Short, medium, long passages
                "tc_blank_types": ["TC_1", "TC_2", "TC_3"],    # 1, 2, 3 blanks
                "themes": ["science", "humanities", "social_sciences", "literature", "history"]
            }
        }
        
        if section_type not in configs:
            raise ValueError(f"Unsupported section type for GRE: {section_type}")
        
        return configs[section_type]
    
    def get_question_distribution(self, section_type: SectionType) -> Dict[str, int]:
        """Get question distribution for GRE sections."""
        if section_type == SectionType.QUANTITATIVE:
            return {
                "PS": 8,   # Problem Solving
                "QC": 3,   # Quantitative Comparison (Data Sufficiency style)
                "NE": 2,   # Numeric Entry
                "PC": 2    # Parent-Child (shared data)
            }
        
        elif section_type == SectionType.VERBAL:
            return {
                "RC": 4,   # Reading Comprehension
                "TC": 6,   # Text Completion
                "SE": 5    # Sentence Equivalence
            }
        
        else:
            raise ValueError(f"Unsupported section type for GRE: {section_type}")
    
    def get_total_questions(self) -> int:
        """Get total number of questions for GRE."""
        total_quant = self.quant_sections * self.questions_per_quant_section
        total_verbal = self.verbal_sections * self.questions_per_verbal_section
        return total_quant + total_verbal
    
    def get_time_limits(self) -> Dict[SectionType, int]:
        """Get time limits for GRE sections in minutes."""
        return {
            SectionType.QUANTITATIVE: 35,  # Per section
            SectionType.VERBAL: 30         # Per section
        }
    
    def get_total_time_limit(self) -> int:
        """Get total time limit for the entire exam."""
        quant_time = self.quant_sections * 35
        verbal_time = self.verbal_sections * 30
        return quant_time + verbal_time  # Plus breaks in real exam
    
    def get_section_weight(self, section_type: SectionType) -> float:
        """Get section weight for GRE scoring."""
        # Quantitative and Verbal are equally weighted in GRE
        return 0.5
    
    def get_difficulty_adjustment(self, section_type: SectionType) -> float:
        """Get difficulty adjustment factor for different sections."""
        # GRE sections are generally balanced in difficulty
        adjustments = {
            SectionType.QUANTITATIVE: 1.0,
            SectionType.VERBAL: 1.0
        }
        
        return adjustments.get(section_type, 1.0)
    
    def get_adaptive_parameters(self) -> Dict[str, Any]:
        """Get parameters for adaptive testing simulation."""
        return {
            "enable_adaptive": True,
            "section_adaptive": True,        # GRE is section-level adaptive
            "difficulty_adjustment_factor": 0.4,
            "min_questions_before_adjustment": 0,  # Adjustment happens between sections
            "max_difficulty_change": 2,     # Can change significantly between sections
            "target_success_rate": 0.5      # Target 50% success rate
        }
    
    def get_section_order(self) -> List[str]:
        """Get the order of sections in the exam."""
        # GRE typically alternates sections, but can vary
        return [
            "verbal_1",
            "quantitative_1", 
            "verbal_2",
            "quantitative_2"
        ]
    
    def get_passage_distribution(self) -> Dict[str, Any]:
        """Get reading comprehension passage distribution."""
        return {
            "passages_per_section": 2,  # Typically 2 passages per verbal section
            "passage_types": {
                "short": {"questions": 1, "probability": 0.3},
                "medium": {"questions": 2, "probability": 0.5},
                "long": {"questions": 3, "probability": 0.2}
            },
            "themes": [
                "science", "humanities", "social_sciences", 
                "literature", "history", "current_events"
            ]
        }
    
    def get_text_completion_distribution(self) -> Dict[str, Any]:
        """Get text completion question distribution."""
        return {
            "blank_distribution": {
                1: 3,  # 3 questions with 1 blank
                2: 2,  # 2 questions with 2 blanks  
                3: 1   # 1 question with 3 blanks
            },
            "difficulty_by_blanks": {
                1: "easier",
                2: "medium", 
                3: "harder"
            }
        }
    
    def validate_config(self) -> bool:
        """Validate GRE-specific configuration."""
        # Check section counts
        if not (1 <= self.quant_sections <= 3):
            return False
        
        if not (1 <= self.verbal_sections <= 3):
            return False
        
        # Check questions per section
        if not (10 <= self.questions_per_quant_section <= 25):
            return False
        
        if not (10 <= self.questions_per_verbal_section <= 25):
            return False
        
        # Check total time is reasonable
        total_time = self.get_total_time_limit()
        if not (60 <= total_time <= 180):  # 1 to 3 hours
            return False
        
        return True