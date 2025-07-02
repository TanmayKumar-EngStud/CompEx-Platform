"""
GMAT Exam Configuration Module.

This module provides GMAT-specific configuration including section requirements,
question distributions, and timing parameters.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from .base_exam_config import BaseExamConfig


@dataclass
class GMATConfig(BaseExamConfig):
    """
    GMAT-specific exam configuration.
    
    Defines the structure, requirements, and parameters for GMAT exams including
    the three main sections: Quantitative, Verbal, and Integrated Reasoning.
    
    Attributes:
        include_integrated_reasoning: Whether to include IR section
        quant_questions: Number of quantitative questions
        verbal_questions: Number of verbal questions  
        ir_questions: Number of integrated reasoning questions
    """
    
    include_integrated_reasoning: bool = True
    quant_questions: int = 21
    verbal_questions: int = 23
    ir_questions: int = 8
    
    def __post_init__(self):
        """Initialize GMAT-specific configuration."""
        # Set GMAT-specific defaults
        self.exam_type = ExamType.GMAT
        
        # Define GMAT sections
        if self.include_integrated_reasoning:
            self.sections = [
                SectionType.QUANTITATIVE,
                SectionType.VERBAL,
                SectionType.INTEGRATED_REASONING
            ]
        else:
            self.sections = [
                SectionType.QUANTITATIVE,
                SectionType.VERBAL
            ]
        
        # Call parent validation
        super().__post_init__()
    
    @classmethod
    def from_difficulty(cls, difficulty: int) -> 'GMATConfig':
        """
        Create GMAT configuration from difficulty level.
        
        Args:
            difficulty: Difficulty level (1-5)
            
        Returns:
            Configured GMAT instance
        """
        return cls(
            exam_type=ExamType.GMAT,
            difficulty=difficulty,
            sections=[],  # Will be set in __post_init__
            max_workers=10,
            api_instances=5,
            requests_per_instance=60,
            time_window=60,
            include_integrated_reasoning=True,
            quant_questions=21,
            verbal_questions=23,
            ir_questions=8
        )
    
    def get_section_config(self, section_type: SectionType) -> Dict[str, Any]:
        """Get GMAT section-specific configuration."""
        configs = {
            SectionType.QUANTITATIVE: {
                "question_count": self.quant_questions,
                "time_limit_minutes": 75,
                "question_types": ["DS", "PS"],  # Data Sufficiency, Problem Solving
                "topics": ["arithmetic", "algebra", "geometry", "word_problems", "data_analysis"],
                "ds_percentage": 0.4,  # 40% Data Sufficiency, 60% Problem Solving
                "ps_percentage": 0.6
            },
            SectionType.VERBAL: {
                "question_count": self.verbal_questions,
                "time_limit_minutes": 75,
                "question_types": ["RC", "CR"],  # Reading Comprehension, Critical Reasoning
                "rc_questions": [13, 14],  # Variable RC questions
                "cr_questions": [9, 10],   # Variable CR questions
                "rc_passage_types": ["RC_3", "RC_4"],  # 3 or 4 questions per passage
                "themes": ["business", "science", "history", "literature", "sociology", "economics"]
            },
            SectionType.INTEGRATED_REASONING: {
                "question_count": self.ir_questions,
                "time_limit_minutes": 30,
                "question_types": ["GI", "TPA", "TA", "MSR"],
                "questions_per_type": 2,  # 2 questions of each IR type
                "chart_types": ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"],
                "data_sources": ["tables", "graphs", "text", "charts"]
            }
        }
        
        if section_type not in configs:
            raise ValueError(f"Unsupported section type for GMAT: {section_type}")
        
        return configs[section_type]
    
    def get_question_distribution(self, section_type: SectionType) -> Dict[str, int]:
        """Get question distribution for GMAT sections."""
        if section_type == SectionType.QUANTITATIVE:
            ds_count = int(self.quant_questions * 0.4)  # 40% DS
            ps_count = self.quant_questions - ds_count   # 60% PS
            return {"DS": ds_count, "PS": ps_count}
        
        elif section_type == SectionType.VERBAL:
            # Variable distribution
            rc_count = 13  # Can be 13 or 14
            cr_count = self.verbal_questions - rc_count
            return {"RC": rc_count, "CR": cr_count}
        
        elif section_type == SectionType.INTEGRATED_REASONING:
            return {"GI": 2, "TPA": 2, "TA": 2, "MSR": 2}
        
        else:
            raise ValueError(f"Unsupported section type for GMAT: {section_type}")
    
    def get_total_questions(self) -> int:
        """Get total number of questions for GMAT."""
        total = self.quant_questions + self.verbal_questions
        if self.include_integrated_reasoning:
            total += self.ir_questions
        return total
    
    def get_time_limits(self) -> Dict[SectionType, int]:
        """Get time limits for GMAT sections in minutes."""
        limits = {
            SectionType.QUANTITATIVE: 75,
            SectionType.VERBAL: 75
        }
        
        if self.include_integrated_reasoning:
            limits[SectionType.INTEGRATED_REASONING] = 30
        
        return limits
    
    def get_section_weight(self, section_type: SectionType) -> float:
        """Get section weight for GMAT scoring."""
        if section_type in [SectionType.QUANTITATIVE, SectionType.VERBAL]:
            return 0.45  # Quant and Verbal are equally weighted and primary
        elif section_type == SectionType.INTEGRATED_REASONING:
            return 0.1   # IR has lower weight
        else:
            return 0.0
    
    def get_difficulty_adjustment(self, section_type: SectionType) -> float:
        """Get difficulty adjustment factor for different sections."""
        # GMAT sections can have different difficulty curves
        adjustments = {
            SectionType.QUANTITATIVE: 1.0,     # Standard difficulty
            SectionType.VERBAL: 1.1,           # Slightly harder on average
            SectionType.INTEGRATED_REASONING: 0.9  # Slightly easier
        }
        
        return adjustments.get(section_type, 1.0)
    
    def get_adaptive_parameters(self) -> Dict[str, Any]:
        """Get parameters for adaptive testing simulation."""
        return {
            "enable_adaptive": True,
            "difficulty_adjustment_factor": 0.3,
            "min_questions_before_adjustment": 5,
            "max_difficulty_change": 1,  # Max change in difficulty level per adjustment
            "target_success_rate": 0.6    # Target 60% success rate
        }
    
    def validate_config(self) -> bool:
        """Validate GMAT-specific configuration."""
        # Check question counts are reasonable
        if not (15 <= self.quant_questions <= 35):
            return False
        
        if not (15 <= self.verbal_questions <= 40):
            return False
        
        if self.include_integrated_reasoning and not (6 <= self.ir_questions <= 15):
            return False
        
        # Check total time is reasonable (should be around 3-4 hours)
        total_time = sum(self.get_time_limits().values())
        if not (150 <= total_time <= 240):  # 2.5 to 4 hours
            return False
        
        return True