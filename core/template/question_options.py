"""
QuestionOptions template class for handling options generation templates.

This class manages question options template loading and processing,
including various option formats like dichotomous choice, sentence equivalence, etc.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from core.instructions.template_processor import TemplateProcessor


class QuestionOptions:
    """
    Handles question options template loading and processing.
    
    This class provides methods for different option formats,
    including dichotomous choice, sentence equivalence, and multiple choice variations.
    """
    
    def __init__(self):
        """Initialize the QuestionOptions handler."""
        self._logger = StructuredLogger(__name__)
        self._template_processor = TemplateProcessor()
        
    def generic(
        self, 
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load generic question options template from 4-questionOptions/0-generic.txt.template
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed generic question options template
        """
        template = self._load_template_file("4-questionOptions/0-generic.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
    def dichotomous_choice(
        self,
        exam_type: ExamType, 
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load dichotomous choice options template from 4-questionOptions/1-dichotomous-choice.txt.template
        
        Handles Yes/No, True/False, and similar binary choice formats.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed dichotomous choice options template with token replacement
        """
        template = self._load_template_file("4-questionOptions/1-dichotomous-choice.txt.template")
        
        # Apply dichotomous choice token replacement
        processed_template = self._apply_dichotomous_tokens(template, prompt)
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def sentence_equivalence(
        self,
        exam_type: ExamType,
        question_type: QuestionType, 
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load sentence equivalence options template from 4-questionOptions/2-sentence_equivalence.txt.template
        
        Handles GRE sentence equivalence question format.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed sentence equivalence options template
        """
        template = self._load_template_file("4-questionOptions/2-sentence_equivalence.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
    def text_completion(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load text completion options template from 4-questionOptions/3-text_completion.txt.template
        
        Handles GRE text completion question format.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed text completion options template
        """
        template = self._load_template_file("4-questionOptions/3-text_completion.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
    def mcq_multiple(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load multiple choice (multiple answers) options template from 4-questionOptions/4-mcq_multiple.txt.template
        
        Handles multiple choice questions with multiple correct answers.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed multiple choice options template
        """
        template = self._load_template_file("4-questionOptions/4-mcq_multiple.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
    def _apply_dichotomous_tokens(self, template: str, prompt: Optional[str] = None) -> str:
        """
        Apply dichotomous choice token replacement to template.
        
        Replaces {type} token with appropriate dichotomous choice type
        (Yes/No, True/False, etc.) based on prompt content.
        
        Args:
            template: Raw template content
            prompt: Original prompt for context
            
        Returns:
            Template with {type} tokens replaced
        """
        try:
            if not prompt:
                # Default to Yes/No if no prompt context
                return template.replace("{type}", "Yes/No")
            
            prompt_lower = prompt.lower()
            
            # Map prompt keywords to dichotomous choice types
            choice_types = {
                "true": "True/False",
                "false": "True/False", 
                "correct": "Correct/Incorrect",
                "accurate": "Accurate/Inaccurate",
                "valid": "Valid/Invalid",
                "agree": "Agree/Disagree",
                "support": "Support/Oppose"
            }
            
            for keyword, choice_type in choice_types.items():
                if keyword in prompt_lower:
                    return template.replace("{type}", choice_type)
            
            # Default to Yes/No
            return template.replace("{type}", "Yes/No")
            
        except Exception as e:
            self._logger.error(f"Failed to apply dichotomous tokens: {e}")
            return template.replace("{type}", "Yes/No")
    
    def _load_template_file(self, template_path: str) -> str:
        """
        Load template file from system_instructions/templates directory.
        
        Args:
            template_path: Relative path to template file
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file can't be read
        """
        full_path = Path("system_instructions/templates") / template_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Template file not found: {full_path}")
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._logger.debug(f"Loaded template: {template_path}")
            return content
        except Exception as e:
            raise IOError(f"Failed to load template {template_path}: {e}")