"""
QuestionTitle template class for handling title generation templates.

This class manages question title template loading and processing.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from core.instructions.template_processor import TemplateProcessor


class QuestionTitle:
    """
    Handles question title template loading and processing.
    
    This class provides methods for question title generation.
    """
    
    def __init__(self):
        """Initialize the QuestionTitle handler."""
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
        Load generic question title template from 2-questionTitle/0-generic.txt.template
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed generic question title template
        """
        template = self._load_template_file("2-questionTitle/0-generic.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
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