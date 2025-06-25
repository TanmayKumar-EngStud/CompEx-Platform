"""
Base configuration classes for exam-specific settings.

This module provides the foundation for managing exam-specific configurations
in a type-safe and extensible manner.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from ..enums.exam_types import ExamType
from ..enums.section_types import SectionType
from ..enums.question_types import QuestionType


@dataclass
class BaseExamConfig(ABC):
    """
    Abstract base class for exam-specific configurations.
    
    This class defines the common interface and functionality that all
    exam configurations must implement.
    """
    
    exam_type: ExamType
    debug_mode: bool = False
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 300
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BaseExamConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            Configuration instance
        """
        pass
    
    @abstractmethod
    def get_section_question_counts(self) -> Dict[SectionType, int]:
        """
        Get the number of questions for each section.
        
        Returns:
            Dictionary mapping section types to question counts
        """
        pass
    
    @abstractmethod
    def get_supported_question_types(self, section_type: SectionType) -> List[QuestionType]:
        """
        Get supported question types for a section.
        
        Args:
            section_type: Section to get question types for
            
        Returns:
            List of supported question types
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Enum):
                result[field_name] = field_value.value
            else:
                result[field_name] = field_value
        return result
    
    def get_timeout_minutes(self) -> float:
        """
        Get timeout in minutes.
        
        Returns:
            Timeout value in minutes
        """
        return self.timeout_seconds / 60.0
    
    def is_debug_enabled(self) -> bool:
        """
        Check if debug mode is enabled.
        
        Returns:
            True if debug mode is enabled
        """
        return self.debug_mode
    
    def get_log_level_numeric(self) -> int:
        """
        Get numeric log level for logging configuration.
        
        Returns:
            Numeric log level
        """
        import logging
        return getattr(logging, self.log_level.upper(), logging.INFO)


@dataclass
class GMATConfig(BaseExamConfig):
    """
    GMAT-specific configuration settings.
    """
    
    # Section-specific settings
    include_integrated_reasoning: bool = True
    quant_questions_per_section: int = 31
    verbal_questions_per_section: int = 36
    ir_questions_per_section: int = 12
    
    # Question type distributions
    quant_ds_percentage: float = 0.5  # 50% Data Sufficiency in Quants
    verbal_rc_percentage: float = 0.4  # 40% Reading Comprehension in Verbal
    verbal_cr_percentage: float = 0.35  # 35% Critical Reasoning in Verbal
    verbal_sc_percentage: float = 0.25  # 25% Sentence Correction in Verbal
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.exam_type != ExamType.GMAT:
            self.exam_type = ExamType.GMAT
    
    def validate(self) -> bool:
        """
        Validate GMAT configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check positive question counts
        if (self.quant_questions_per_section <= 0 or 
            self.verbal_questions_per_section <= 0):
            return False
        
        if self.include_integrated_reasoning and self.ir_questions_per_section <= 0:
            return False
        
        # Check percentage distributions
        verbal_total = (self.verbal_rc_percentage + 
                       self.verbal_cr_percentage + 
                       self.verbal_sc_percentage)
        
        if abs(verbal_total - 1.0) > 0.01:  # Allow small floating point errors
            return False
        
        # Check percentage ranges
        percentages = [self.quant_ds_percentage, self.verbal_rc_percentage,
                      self.verbal_cr_percentage, self.verbal_sc_percentage]
        
        for percentage in percentages:
            if not 0.0 <= percentage <= 1.0:
                return False
        
        return True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GMATConfig':
        """
        Create GMAT config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            GMATConfig instance
        """
        return cls(
            exam_type=ExamType.GMAT,
            debug_mode=config_dict.get('debug_mode', False),
            log_level=config_dict.get('log_level', 'INFO'),
            max_retries=config_dict.get('max_retries', 3),
            timeout_seconds=config_dict.get('timeout_seconds', 300),
            include_integrated_reasoning=config_dict.get('include_integrated_reasoning', True),
            quant_questions_per_section=config_dict.get('quant_questions_per_section', 31),
            verbal_questions_per_section=config_dict.get('verbal_questions_per_section', 36),
            ir_questions_per_section=config_dict.get('ir_questions_per_section', 12),
            quant_ds_percentage=config_dict.get('quant_ds_percentage', 0.5),
            verbal_rc_percentage=config_dict.get('verbal_rc_percentage', 0.4),
            verbal_cr_percentage=config_dict.get('verbal_cr_percentage', 0.35),
            verbal_sc_percentage=config_dict.get('verbal_sc_percentage', 0.25)
        )
    
    def get_section_question_counts(self) -> Dict[SectionType, int]:
        """
        Get the number of questions for each GMAT section.
        
        Returns:
            Dictionary mapping section types to question counts
        """
        result = {
            SectionType.QUANTITATIVE: self.quant_questions_per_section,
            SectionType.VERBAL: self.verbal_questions_per_section
        }
        
        if self.include_integrated_reasoning:
            result[SectionType.INTEGRATED_REASONING] = self.ir_questions_per_section
        
        return result
    
    def get_supported_question_types(self, section_type: SectionType) -> List[QuestionType]:
        """
        Get supported question types for a GMAT section.
        
        Args:
            section_type: Section to get question types for
            
        Returns:
            List of supported question types
        """
        return QuestionType.get_section_questions(section_type, ExamType.GMAT)
    
    def get_question_type_distribution(self, section_type: SectionType) -> Dict[QuestionType, float]:
        """
        Get question type distribution for a section.
        
        Args:
            section_type: Section to get distribution for
            
        Returns:
            Dictionary mapping question types to their proportions
        """
        if section_type == SectionType.QUANTITATIVE:
            return {
                QuestionType.DATA_SUFFICIENCY: self.quant_ds_percentage,
                QuestionType.PROBLEM_SOLVING: 1.0 - self.quant_ds_percentage
            }
        elif section_type == SectionType.VERBAL:
            return {
                QuestionType.READING_COMPREHENSION: self.verbal_rc_percentage,
                QuestionType.CRITICAL_REASONING: self.verbal_cr_percentage,
                QuestionType.SENTENCE_CORRECTION: self.verbal_sc_percentage
            }
        elif section_type == SectionType.INTEGRATED_REASONING:
            # Equal distribution for IR question types
            return {
                QuestionType.GRAPHIC_INTERPRETATION: 0.25,
                QuestionType.TABLE_ANALYSIS: 0.25,
                QuestionType.TWO_PART_ANALYSIS: 0.25,
                QuestionType.MULTI_SOURCE_REASONING: 0.25
            }
        else:
            return {}


@dataclass
class GREConfig(BaseExamConfig):
    """
    GRE-specific configuration settings.
    """
    
    # Section-specific settings
    quant_questions_per_section: int = 20
    verbal_questions_per_section: int = 20
    
    # Question type distributions
    quant_ps_percentage: float = 0.4   # 40% Problem Solving
    quant_ds_percentage: float = 0.3   # 30% Data Sufficiency  
    quant_ne_percentage: float = 0.2   # 20% Numeric Entry
    quant_qc_percentage: float = 0.1   # 10% Quantitative Comparison
    
    verbal_rc_percentage: float = 0.5  # 50% Reading Comprehension
    verbal_tc_percentage: float = 0.3  # 30% Text Completion
    verbal_se_percentage: float = 0.2  # 20% Sentence Equivalence
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.exam_type != ExamType.GRE:
            self.exam_type = ExamType.GRE
    
    def validate(self) -> bool:
        """
        Validate GRE configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check positive question counts
        if (self.quant_questions_per_section <= 0 or 
            self.verbal_questions_per_section <= 0):
            return False
        
        # Check quant percentage distributions
        quant_total = (self.quant_ps_percentage + self.quant_ds_percentage + 
                      self.quant_ne_percentage + self.quant_qc_percentage)
        
        if abs(quant_total - 1.0) > 0.01:  # Allow small floating point errors
            return False
        
        # Check verbal percentage distributions
        verbal_total = (self.verbal_rc_percentage + self.verbal_tc_percentage + 
                       self.verbal_se_percentage)
        
        if abs(verbal_total - 1.0) > 0.01:
            return False
        
        # Check percentage ranges
        percentages = [
            self.quant_ps_percentage, self.quant_ds_percentage,
            self.quant_ne_percentage, self.quant_qc_percentage,
            self.verbal_rc_percentage, self.verbal_tc_percentage,
            self.verbal_se_percentage
        ]
        
        for percentage in percentages:
            if not 0.0 <= percentage <= 1.0:
                return False
        
        return True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GREConfig':
        """
        Create GRE config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            GREConfig instance
        """
        return cls(
            exam_type=ExamType.GRE,
            debug_mode=config_dict.get('debug_mode', False),
            log_level=config_dict.get('log_level', 'INFO'),
            max_retries=config_dict.get('max_retries', 3),
            timeout_seconds=config_dict.get('timeout_seconds', 300),
            quant_questions_per_section=config_dict.get('quant_questions_per_section', 20),
            verbal_questions_per_section=config_dict.get('verbal_questions_per_section', 20),
            quant_ps_percentage=config_dict.get('quant_ps_percentage', 0.4),
            quant_ds_percentage=config_dict.get('quant_ds_percentage', 0.3),
            quant_ne_percentage=config_dict.get('quant_ne_percentage', 0.2),
            quant_qc_percentage=config_dict.get('quant_qc_percentage', 0.1),
            verbal_rc_percentage=config_dict.get('verbal_rc_percentage', 0.5),
            verbal_tc_percentage=config_dict.get('verbal_tc_percentage', 0.3),
            verbal_se_percentage=config_dict.get('verbal_se_percentage', 0.2)
        )
    
    def get_section_question_counts(self) -> Dict[SectionType, int]:
        """
        Get the number of questions for each GRE section.
        
        Returns:
            Dictionary mapping section types to question counts
        """
        return {
            SectionType.QUANTITATIVE: self.quant_questions_per_section,
            SectionType.VERBAL: self.verbal_questions_per_section
        }
    
    def get_supported_question_types(self, section_type: SectionType) -> List[QuestionType]:
        """
        Get supported question types for a GRE section.
        
        Args:
            section_type: Section to get question types for
            
        Returns:
            List of supported question types
        """
        return QuestionType.get_section_questions(section_type, ExamType.GRE)
    
    def get_question_type_distribution(self, section_type: SectionType) -> Dict[QuestionType, float]:
        """
        Get question type distribution for a section.
        
        Args:
            section_type: Section to get distribution for
            
        Returns:
            Dictionary mapping question types to their proportions
        """
        if section_type == SectionType.QUANTITATIVE:
            return {
                QuestionType.PROBLEM_SOLVING: self.quant_ps_percentage,
                QuestionType.DATA_SUFFICIENCY: self.quant_ds_percentage,
                QuestionType.NUMERIC_ENTRY: self.quant_ne_percentage,
                QuestionType.QUANTITATIVE_COMPARISON: self.quant_qc_percentage
            }
        elif section_type == SectionType.VERBAL:
            return {
                QuestionType.READING_COMPREHENSION: self.verbal_rc_percentage,
                QuestionType.TEXT_COMPLETION: self.verbal_tc_percentage,
                QuestionType.SENTENCE_EQUIVALENCE: self.verbal_se_percentage
            }
        else:
            return {}