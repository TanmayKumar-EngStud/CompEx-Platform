"""
Centralized instruction management system for GMAT/GRE question generation.

This module provides comprehensive instruction loading, caching, and template
processing for all question types across both exam systems.
"""

import os
import json
from typing import Dict, Optional, Any, Set
from pathlib import Path

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from .instruction_loader import InstructionLoader
from .template_processor import TemplateProcessor


class InstructionManager:
    """
    Centralized system for managing question generation instructions.
    
    Provides template processing and exam-specific customization
    for all question types and instruction modes.
    
    Attributes:
        _loader: Instruction file loader instance
        _processor: Template processor instance
        _logger: Structured logger instance
        
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
    
    def __init__(self):
        """
        Initialize the instruction manager.
        """
        self._loader = InstructionLoader()
        self._processor = TemplateProcessor()
        self._logger = StructuredLogger(__name__)
        
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
        """Get instruction with fresh generation each time."""
        self._logger.log_instruction_request(exam_type, question_type, mode)
        
        # Load base template
        template = self._loader.load_template(question_type, mode, prompt)
        
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
        
        # First, load the main instruction template (philosophy)
        try:
            main_instruction = self.get_main_instruction(exam_type, question_type)
            instructions.append(main_instruction)
        except Exception:
            # If main instruction fails to load, continue with component instructions
            pass
        
        for mode in sorted(available_modes):
            try:
                mode_instruction = self.get_instruction(exam_type, question_type, mode, prompt)
                instructions.append(mode_instruction)
            except Exception:
                # Skip modes that fail to load
                continue
        
        return "\n\n".join(instructions)
    
    def get_main_instruction(
        self,
        exam_type: ExamType,
        question_type: QuestionType
    ) -> str:
        """
        Get main instruction template (philosophy) for a question type.
        
        Args:
            exam_type: Target exam type (GMAT or GRE)
            question_type: Question type classification
            
        Returns:
            Main instruction text with philosophy and guidelines
            
        Raises:
            InstructionNotFoundError: If main instruction cannot be found
        """
        self._logger.log_instruction_request(exam_type, question_type, "mainInstruction")
        
        # Load main instruction template
        main_template = self._loader.load_main_instruction_template(question_type)
        
        # Get exam-specific customizations
        customizations = self._loader.load_customizations(exam_type, question_type)
        
        # Process template with customizations
        instruction = self._processor.process_template(
            main_template, 
            exam_type, 
            question_type, 
            customizations
        )
        
        self._logger.log_instruction_success(exam_type, question_type, "mainInstruction")
        return instruction
    
    def get_optimized_instruction(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        prompt: Optional[str] = None,
        difficulty_level: Optional[int] = None
    ) -> str:
        """
        Get optimized instruction based on question type characteristics and context.
        
        Args:
            exam_type: Target exam type (GMAT or GRE)
            question_type: Question type classification
            prompt: Optional prompt for context analysis
            difficulty_level: Optional difficulty level (1-5)
            
        Returns:
            Optimized instruction text tailored to the specific context
        """
        # Get base instruction with all modes
        base_instruction = self.get_all_modes_instruction(exam_type, question_type, prompt)
        
        # Apply dynamic optimizations based on question characteristics
        optimized_instruction = self._apply_dynamic_optimizations(
            base_instruction,
            exam_type,
            question_type,
            prompt,
            difficulty_level
        )
        
        return optimized_instruction
    
    def _apply_dynamic_optimizations(
        self,
        instruction: str,
        exam_type: ExamType,
        question_type: QuestionType,
        prompt: Optional[str] = None,
        difficulty_level: Optional[int] = None
    ) -> str:
        """Apply dynamic optimizations to instruction based on context."""
        optimized = instruction
        
        # Apply difficulty-based optimizations
        if difficulty_level:
            optimized = self._apply_difficulty_optimizations(optimized, difficulty_level)
        
        # Apply prompt-based optimizations
        if prompt:
            optimized = self._apply_prompt_optimizations(optimized, prompt, question_type)
        
        # Apply question-type specific optimizations
        optimized = self._apply_question_type_optimizations(optimized, question_type, exam_type)
        
        return optimized
    
    def _apply_difficulty_optimizations(self, instruction: str, difficulty_level: int) -> str:
        """Apply difficulty-based optimizations to instruction."""
        if difficulty_level >= 4:
            # For high difficulty, emphasize trap generation
            emphasis = "\n\n**HIGH DIFFICULTY EMPHASIS:**\n"
            emphasis += "- Create more sophisticated traps that catch students with partial understanding\n"
            emphasis += "- Include multi-step reasoning errors in option generation\n"
            emphasis += "- Ensure distractors require careful analysis to eliminate\n"
            instruction += emphasis
        elif difficulty_level <= 2:
            # For low difficulty, emphasize fundamental concepts
            emphasis = "\n\n**FUNDAMENTAL LEVEL EMPHASIS:**\n"
            emphasis += "- Focus on core concepts without excessive complexity\n"
            emphasis += "- Create clear, educationally sound distractors\n"
            emphasis += "- Ensure question tests basic understanding of the skill\n"
            instruction += emphasis
        
        return instruction
    
    def _apply_prompt_optimizations(self, instruction: str, prompt: str, question_type: QuestionType) -> str:
        """Apply prompt-based optimizations to instruction."""
        prompt_lower = prompt.lower()
        
        # Check for specific skill emphasis
        if "logical reasoning" in prompt_lower:
            instruction += "\n\n**LOGICAL REASONING EMPHASIS:**\n"
            instruction += "- Prioritize logical structure and reasoning chains\n"
            instruction += "- Create options that test different logical pathways\n"
        
        if "data interpretation" in prompt_lower:
            instruction += "\n\n**DATA INTERPRETATION EMPHASIS:**\n"
            instruction += "- Focus on data analysis and interpretation skills\n"
            instruction += "- Create options that test different data reading approaches\n"
        
        # Check for specific content areas
        if any(term in prompt_lower for term in ["graph", "chart", "table"]):
            instruction += "\n\n**VISUAL DATA EMPHASIS:**\n"
            instruction += "- Ensure visual elements are integral to the solution\n"
            instruction += "- Create options that test different visual interpretation methods\n"
        
        return instruction
    
    def _apply_question_type_optimizations(self, instruction: str, question_type: QuestionType, exam_type: ExamType) -> str:
        """Apply question-type specific optimizations."""
        # Parent-child question types need coordination emphasis
        if question_type.is_parent_child_type:
            instruction += "\n\n**PARENT-CHILD COORDINATION:**\n"
            instruction += "- Ensure all child questions relate to the parent stimulus\n"
            instruction += "- Create variety in child question difficulty and focus\n"
            instruction += "- Maintain consistent context across all questions\n"
        
        # Data sufficiency questions need specific emphasis
        if question_type == QuestionType.DATA_SUFFICIENCY:
            instruction += "\n\n**DATA SUFFICIENCY FOCUS:**\n"
            instruction += "- Emphasize sufficiency analysis over computation\n"
            instruction += "- Create options that test different sufficiency reasoning paths\n"
            instruction += "- Ensure statements have clear logical relationships\n"
        
        # Exam-specific optimizations
        if exam_type == ExamType.GMAT:
            instruction += "\n\n**GMAT BUSINESS CONTEXT:**\n"
            instruction += "- Use business scenarios and professional terminology\n"
            instruction += "- Focus on managerial decision-making skills\n"
        elif exam_type == ExamType.GRE:
            instruction += "\n\n**GRE ACADEMIC CONTEXT:**\n"
            instruction += "- Use academic scenarios and scholarly terminology\n"
            instruction += "- Focus on analytical and research skills\n"
        
        return instruction
    
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