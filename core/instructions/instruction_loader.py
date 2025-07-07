"""
Instruction loading system for GMAT/GRE question generation.

This module handles loading instruction templates and exam-specific
customizations from the file system.
"""

import os
import json
from typing import Dict, Optional, Any, List
from pathlib import Path

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from core.utilities.file_utils import load_json_file


class InstructionLoader:
    """
    Loads instruction templates and exam-specific customizations.
    
    Handles the file system interaction for instruction management,
    including template loading and customization data retrieval.
    
    Attributes:
        _logger: Structured logger instance
        _legacy_mode: Whether to use legacy instruction files
        
    Example:
        loader = InstructionLoader()
        template = loader.load_template(QuestionType.DATA_SUFFICIENCY, "questionText")
        customizations = loader.load_customizations(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
    """
    
    
    def __init__(self):
        """Initialize the instruction loader."""
        self._logger = StructuredLogger(__name__)
        
        # Validate that the new system is properly set up
        self._validate_new_system()
    
    def load_template(self, question_type: QuestionType, mode: str) -> str:
        """
        Load instruction template for a question type and mode.
        
        Args:
            question_type: Question type classification
            mode: Instruction mode (e.g., "questionText")
            
        Returns:
            Template content as string
            
        Raises:
            TemplateLoadError: If template loading fails
        """
        return self._load_template_file(question_type, mode)
    
    def load_customizations(
        self, 
        exam_type: ExamType, 
        question_type: QuestionType
    ) -> Dict[str, Any]:
        """
        Load exam-specific customizations for a question type.
        
        Args:
            exam_type: Target exam type
            question_type: Question type classification
            
        Returns:
            Dictionary of customization parameters
        """
        return self._load_customization_file(exam_type, question_type)
    
    def _validate_new_system(self) -> None:
        """Validate that the new instruction system is properly set up."""
        system_instructions_path = Path("system_instructions")
        if not system_instructions_path.exists():
            raise FileNotFoundError("system_instructions directory not found - unified instruction system required")
        
        templates_path = system_instructions_path / "templates"
        if not templates_path.exists():
            raise FileNotFoundError("templates directory not found - unified instruction system required")
        
        # Check for required customization files
        gmat_customizations = system_instructions_path / "gmat" / "customizations.json"
        gre_customizations = system_instructions_path / "gre" / "customizations.json"
        
        if not gmat_customizations.exists():
            raise FileNotFoundError("GMAT customizations file not found - unified instruction system required")
        
        if not gre_customizations.exists():
            raise FileNotFoundError("GRE customizations file not found - unified instruction system required")
    
    def _load_template_file(self, question_type: QuestionType, mode: str) -> str:
        """Load template from centralized template system."""
        
        component_map = {
            "questionPassage": "0-questionMetadata",
            "questionGraph": "0-questionMetadata",
            "parentStimulus": "0-questionMetadata", 
            "multiSource": "0-questionMetadata",
            "specializedTable": "0-questionMetadata",
            "questionText": "1-questionText",
            "childQuestion": "1-questionText",
            "questionTitle": "2-questionTitle",
            "questionOptions": "3-questionOptions",
            "dichotomousChoiceOptions": "3-questionOptions",
            "questionSolution": "4-questionSolution",
            "questionAnswer": "5-questionAnswer",
        }

        question_style_map = {
            "generic": "0-generic",
            "data_sufficiency": "1-data_sufficiency",
            "numeric_entry": "2-numeric_entry",
            "passage": "0-passage",
            "graph": "1-graph",
            "parent_stimulus": "2-parent_stimulus",
            "child_question": "3-child_question",
            "multi_source": "3-multi_source",
            "dichotomous_choice": "1-dichotomous_choice",
            "specialized_table": "4-specialized_table",
            "sentence_equivalence": "2-sentence_equivalence",
            "text_completion": "3-text_completion"
        }
        
        component_folder = component_map.get(mode)
        if not component_folder:
            raise TemplateLoadError(f"Invalid mode: {mode}")

        question_style = question_type.value
        if mode in ["questionPassage", "questionGraph", "parentStimulus", "multiSource", "specializedTable", "childQuestion", "dichotomousChoiceOptions"]:
             style_key_map = {
                "questionPassage": "passage",
                "questionGraph": "graph",
                "parentStimulus": "parent_stimulus",
                "childQuestion": "child_question",
                "multiSource": "multi_source",
                "dichotomousChoiceOptions": "dichotomous_choice",
                "specializedTable": "specialized_table"
             }
             question_style = style_key_map.get(mode, question_type.value)


        question_style_filename = question_style_map.get(question_style, "0-generic")

        template_path = Path("system_instructions") / "templates" / component_folder / f"{question_style_filename}.txt.template"

        if not template_path.exists():
            # Fall back to generic template in the same component folder
            template_path = Path("system_instructions") / "templates" / component_folder / "0-generic.txt.template"
        
        if not template_path.exists():
            raise TemplateLoadError(f"Template not found for mode '{mode}' and question_type '{question_type.value}'")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._logger.log_template_loaded(str(template_path))
            return content
        except Exception as e:
            raise TemplateLoadError(f"Failed to load template {template_path}: {e}")

    def _load_customization_file(
        self, 
        exam_type: ExamType, 
        question_type: QuestionType
    ) -> Dict[str, Any]:
        """Load customizations from centralized customization system."""
        customization_path = Path("system_instructions") / exam_type.value / "customizations.json"
        
        if not customization_path.exists():
            self._logger.log_customization_not_found(str(customization_path))
            return {}
        
        try:
            customizations = load_json_file(str(customization_path))
            question_customizations = customizations.get(question_type.value, {})
            self._logger.log_customization_loaded(str(customization_path), len(question_customizations))
            return question_customizations
        except Exception as e:
            self._logger.log_customization_error(e, str(customization_path))
            return {}


    def get_available_templates(self) -> List[str]:
        """
        Get list of available instruction templates.
        
        Returns:
            List of available template names
        """
        templates_path = Path("system_instructions") / "templates"
        if not templates_path.exists():
            return []
        
        templates = []
        for template_file in templates_path.glob("**/*.txt.template"):
            # Construct a representative name, e.g., "0-questionMetadata/0-passage"
            relative_path = template_file.relative_to(templates_path)
            template_name = str(relative_path.with_suffix('').with_suffix(''))
            templates.append(template_name)
        
        return sorted(templates)
    
    def get_available_customizations(self, exam_type: ExamType) -> List[str]:
        """
        Get list of available customizations for an exam type.
        
        Args:
            exam_type: Target exam type
            
        Returns:
            List of available customization keys
        """
        customization_path = Path("system_instructions") / exam_type.value / "customizations.json"
        if not customization_path.exists():
            return []
        
        try:
            customizations = load_json_file(str(customization_path))
            return list(customizations.keys())
        except Exception:
            return []
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get loader system information.
        
        Returns:
            Dictionary containing loader status and statistics
        """
        return {
            "unified_mode": True,
            "available_templates": len(self.get_available_templates()),
            "gmat_customizations": len(self.get_available_customizations(ExamType.GMAT)),
            "gre_customizations": len(self.get_available_customizations(ExamType.GRE))
        }


class TemplateLoadError(Exception):
    """Raised when template loading fails."""
    pass