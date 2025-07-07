"""
Centralized instruction management system for GMAT/GRE question generation.

This module provides comprehensive instruction loading, caching, and template
processing for all question types across both exam systems.
"""

import os
import json
from typing import Dict, Optional, Any, Set
from functools import lru_cache
from pathlib import Path

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from .instruction_loader import InstructionLoader
from .template_processor import TemplateProcessor


class InstructionManager:
    """
    Centralized system for managing question generation instructions.
    
    Provides caching, template processing, and exam-specific customization
    for all question types and instruction modes.
    
    Attributes:
        _loader: Instruction file loader instance
        _processor: Template processor instance
        _logger: Structured logger instance
        _cache_enabled: Whether instruction caching is enabled
        
    Example:
        manager = InstructionManager()
        instruction = manager.get_instruction(
            ExamType.GMAT, 
            QuestionType.DATA_SUFFICIENCY,
            "questionText"
        )
    """
    
    # Standard instruction modes across all question types
    STANDARD_MODES = {
        "questionText",
        "questionTitle", 
        "questionSolution",
        "questionAnswer"
    }
    
    # Question-specific modes
    SPECIALIZED_MODES = {
        QuestionType.CRITICAL_REASONING: {"questionPassage", "questionOptions"},
        QuestionType.READING_COMPREHENSION: {"parentStimulus", "childQuestion", "questionOptions"},
        QuestionType.GRAPHIC_INTERPRETATION: {"questionGraph", "questionOptions"},
        QuestionType.TABLE_ANALYSIS: {"specializedTable", "dichotomousChoiceOptions", "questionOptions"},
        QuestionType.TWO_PART_ANALYSIS: {"questionOptions"},
        QuestionType.MULTI_SOURCE_REASONING: {"multiSource", "childQuestion", "questionOptions"},
        QuestionType.SENTENCE_EQUIVALENCE: {"questionOptions"},
        QuestionType.TEXT_COMPLETION: {"questionOptions"}
    }
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize the instruction manager.
        
        Args:
            cache_enabled: Whether to enable instruction caching (default: True)
        """
        self._loader = InstructionLoader()
        self._processor = TemplateProcessor()
        self._logger = StructuredLogger(__name__)
        self._cache_enabled = cache_enabled
        
        # Initialize and validate system
        self._validate_instruction_system()
    
    def get_instruction(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        mode: str,
        prompt: Optional[str] = None
    ) -> str:
        """
        Get instruction text for a specific exam type, question type, and mode.
        
        Args:
            exam_type: Target exam type (GMAT or GRE)
            question_type: Question type classification
            mode: Instruction mode (e.g., "questionText", "questionTitle")
            prompt: Optional prompt for graph style detection
            
        Returns:
            Processed instruction text ready for AI model
            
        Raises:
            InstructionNotFoundError: If instruction cannot be found
            TemplateProcessingError: If template processing fails
        """
        if self._cache_enabled and not prompt:
            # Only use cache if no prompt is provided (graph styles are dynamic)
            return self._get_instruction_cached(exam_type, question_type, mode)
        else:
            return self._get_instruction_direct(exam_type, question_type, mode, prompt)
    
    @lru_cache(maxsize=256)
    def _get_instruction_cached(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        mode: str
    ) -> str:
        """Get instruction with caching enabled."""
        return self._get_instruction_direct(exam_type, question_type, mode, None)
    
    def _get_instruction_direct(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        mode: str,
        prompt: Optional[str] = None
    ) -> str:
        """Get instruction without caching."""
        self._logger.log_instruction_request(exam_type, question_type, mode)
        
        # Load base template
        template = self._loader.load_template(question_type, mode)
        
        # Get exam-specific customizations
        customizations = self._loader.load_customizations(exam_type, question_type)
        
        # Process template with customizations
        instruction = self._processor.process_template(
            template, 
            exam_type, 
            question_type, 
            customizations,
            prompt
        )
        
        self._logger.log_instruction_success(exam_type, question_type, mode)
        return instruction
    
    def get_available_modes(self, question_type: QuestionType) -> Set[str]:
        """
        Get all available instruction modes for a question type.
        
        Args:
            question_type: Question type classification
            
        Returns:
            Set of available instruction modes
        """
        modes = set(self.STANDARD_MODES)
        
        # Add specialized modes if available
        if question_type in self.SPECIALIZED_MODES:
            modes.update(self.SPECIALIZED_MODES[question_type])
            
        return modes
    
    def get_all_modes_instruction(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        prompt: Optional[str] = None
    ) -> str:
        """
        Get concatenated instruction containing ALL modes for a question type.
        
        Args:
            exam_type: Target exam type (GMAT or GRE)
            question_type: Question type classification
            prompt: Optional prompt for graph style detection
            
        Returns:
            Concatenated instruction text for all modes
        """
        available_modes = self.get_available_modes(question_type)
        
        instructions = []
        for mode in sorted(available_modes):
            try:
                mode_instruction = self._get_instruction_direct(exam_type, question_type, mode, prompt)
                instructions.append(mode_instruction)
            except Exception:
                # Skip modes that fail to load
                continue
        
        return "\n\n".join(instructions)
    
    def validate_mode(self, question_type: QuestionType, mode: str) -> bool:
        """
        Validate if a mode is available for a question type.
        
        Args:
            question_type: Question type classification
            mode: Instruction mode to validate
            
        Returns:
            True if mode is valid, False otherwise
        """
        available_modes = self.get_available_modes(question_type)
        return mode in available_modes
    
    def clear_cache(self) -> None:
        """Clear all cached instructions."""
        if hasattr(self, '_get_instruction_cached'):
            self._get_instruction_cached.cache_clear()
        self._logger.log_cache_cleared()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache hit/miss statistics
        """
        if hasattr(self, '_get_instruction_cached'):
            cache_info = self._get_instruction_cached.cache_info()
            return {
                "hits": cache_info.hits,
                "misses": cache_info.misses,
                "maxsize": cache_info.maxsize,
                "currsize": cache_info.currsize,
                "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0
            }
        return {"cache_enabled": False}
    
    def preload_instructions(
        self, 
        exam_types: Optional[Set[ExamType]] = None,
        question_types: Optional[Set[QuestionType]] = None
    ) -> None:
        """
        Preload instructions into cache for faster access.
        
        Args:
            exam_types: Exam types to preload (default: all)
            question_types: Question types to preload (default: all)
        """
        if not self._cache_enabled:
            self._logger.log_preload_skipped()
            return
            
        exam_types = exam_types or set(ExamType)
        question_types = question_types or set(QuestionType)
        
        preload_count = 0
        for exam_type in exam_types:
            for question_type in question_types:
                available_modes = self.get_available_modes(question_type)
                for mode in available_modes:
                    try:
                        self.get_instruction(exam_type, question_type, mode)
                        preload_count += 1
                    except Exception as e:
                        self._logger.log_preload_error(e, exam_type, question_type, mode)
        
        self._logger.log_preload_completed(preload_count)
    
    def _validate_instruction_system(self) -> None:
        """Validate that the instruction system is properly configured."""
        # Check if system_instructions directory exists
        instructions_path = Path("system_instructions")
        if not instructions_path.exists():
            raise FileNotFoundError("system_instructions directory not found - unified instruction system required")
        
        # Validate template structure
        templates_path = instructions_path / "templates"
        if not templates_path.exists():
            raise FileNotFoundError("templates directory not found - unified instruction system required")
            
        # Count available templates
        template_count = len(list(templates_path.glob("**/*.txt.template")))
        if template_count == 0:
            raise FileNotFoundError("No instruction templates found - unified instruction system required")
            
        self._logger.log_system_validation(template_count)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary containing system status and statistics
        """
        return {
            "cache_enabled": self._cache_enabled,
            "cache_info": self.get_cache_info(),
            "available_question_types": len(QuestionType),
            "available_exam_types": len(ExamType),
            "total_possible_instructions": len(ExamType) * len(QuestionType) * len(self.STANDARD_MODES),
            "loader_info": self._loader.get_system_info(),
            "processor_info": self._processor.get_system_info()
        }


class InstructionNotFoundError(Exception):
    """Raised when a requested instruction cannot be found."""
    
    def __init__(self, exam_type: ExamType, question_type: QuestionType, mode: str):
        self.exam_type = exam_type
        self.question_type = question_type
        self.mode = mode
        super().__init__(
            f"Instruction not found: {exam_type.value}/{question_type.value}/{mode}"
        )


class TemplateProcessingError(Exception):
    """Raised when template processing fails."""
    pass