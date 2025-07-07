"""
Template processing system for GMAT/GRE question generation.

This module handles template processing, variable substitution,
and exam-specific customization application.
"""

import re
from typing import Dict, Any, Optional, List
from string import Template
from pathlib import Path

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from .graph_style_manager import GraphStyleManager


class TemplateProcessor:
    """
    Processes instruction templates with exam-specific customizations.
    
    Handles variable substitution, conditional content, and exam-specific
    customization application for instruction templates.
    
    Attributes:
        _logger: Structured logger instance
        
    Example:
        processor = TemplateProcessor()
        processed = processor.process_template(
            template, 
            ExamType.GMAT, 
            QuestionType.DATA_SUFFICIENCY,
            customizations
        )
    """
    
    # Default template variables
    DEFAULT_VARIABLES = {
        "JSON_FORMAT_REQUIREMENT": '''**STANDARD RESPONSE FORMAT:**
- ALL responses MUST be wrapped in ```json code blocks
- Format: ```json\\n{your json data}\\n```
- Never return raw JSON without the ```json wrapper
- This ensures proper parsing by the system

**Important Notes:**
- Use double quotes only, replace single quotes with (`) symbol
- Ensure all JSON is properly formatted and parseable
- Include all required fields as specified in the output format''',

        "DOUBLE_QUOTE_REQUIREMENT": '''Important Note:
Strictly respond in json format, don't use single quote, always use double quote instead of using single quote use (`) symbol. Both key and value should be enclosed in double quotes.''',
        
        "SOLUTION_PLAIN_TEXT_FORMAT": '''**IMPORTANT - SOLUTION FORMAT:**
- The solution field will be extracted as PLAIN TEXT, not as formatted JSON
- Do NOT use any special tags like <br>, <strong>, or mathematical symbol tags
- Use regular line breaks, mathematical symbols, and formatting directly
- Write the solution as you would naturally explain it to a student
- Use standard mathematical notation (√, π, ≈, ≤, ≥, etc.) directly
- Use regular formatting (bold, italics, etc.) as needed''',
        
        "DATA_SUFFICIENCY_OPTIONS": '''A: "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."
B: "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient."
C: "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."
D: "EITHER statement ALONE is sufficient."
E: "Statements (1) and (2) TOGETHER are NOT sufficient."'''
    }
    
    def __init__(self):
        """Initialize the template processor."""
        self._logger = StructuredLogger(__name__)
        self._graph_style_manager = GraphStyleManager()
    
    def process_template(
        self,
        template: str,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Process a template with exam-specific customizations.
        
        Args:
            template: Raw template content
            exam_type: Target exam type
            question_type: Question type classification
            customizations: Exam-specific customization parameters
            prompt: Optional prompt for graph style detection
            
        Returns:
            Processed instruction text
            
        Raises:
            TemplateProcessingError: If template processing fails
        """
        try:
            # Prepare template variables
            variables = self._prepare_variables(exam_type, question_type, customizations)
            
            # Process conditional content
            processed = self._process_conditionals(template, exam_type, question_type)
            
            # Process template inheritance (e.g., {{GENERIC_PHILOSOPHY_TEMPLATE}})
            processed = self._process_template_inheritance(processed)
            
            # Apply graph style injection if prompt is provided
            if prompt:
                processed = self._graph_style_manager.inject_graph_style(processed, prompt)
            
            # Apply variable substitution
            processed = self._apply_variables(processed, variables)
            
            # Post-process the template
            processed = self._post_process(processed, exam_type, question_type)
            
            self._logger.log_template_processed(exam_type, question_type)
            return processed
            
        except Exception as e:
            self._logger.log_template_processing_error(e, exam_type, question_type)
            raise TemplateProcessingError(f"Template processing failed: {e}")
    
    def _prepare_variables(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Prepare template variables for substitution."""
        variables = dict(self.DEFAULT_VARIABLES)
        
        # Add exam-specific variables
        variables.update({
            "EXAM_NAME": exam_type.value.upper(),
            "EXAM_TYPE": exam_type.value,
            "QUESTION_TYPE": question_type.value,
            "QUESTION_TYPE_DISPLAY": self._get_question_type_display(question_type)
        })
        
        # Add difficulty-related variables
        variables.update(self._get_difficulty_variables(exam_type))
        
        # Add question-specific variables
        variables.update(self._get_question_specific_variables(question_type))
        
        # Apply customizations
        if customizations:
            variables.update(customizations)
        
        return variables
    
    def _process_conditionals(
        self,
        template: str,
        exam_type: ExamType,
        question_type: QuestionType
    ) -> str:
        """Process conditional content blocks in template."""
        # Handle exam-specific conditionals
        template = self._process_exam_conditionals(template, exam_type)
        
        # Handle question-type conditionals
        template = self._process_question_type_conditionals(template, question_type)
        
        return template
    
    def _process_exam_conditionals(self, template: str, exam_type: ExamType) -> str:
        """Process exam-specific conditional blocks."""
        # Process GMAT-only blocks
        gmat_pattern = r'{{#if_gmat}}(.*?){{/if_gmat}}'
        if exam_type == ExamType.GMAT:
            template = re.sub(gmat_pattern, r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(gmat_pattern, '', template, flags=re.DOTALL)
        
        # Process GRE-only blocks
        gre_pattern = r'{{#if_gre}}(.*?){{/if_gre}}'
        if exam_type == ExamType.GRE:
            template = re.sub(gre_pattern, r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(gre_pattern, '', template, flags=re.DOTALL)
        
        return template
    
    def _process_question_type_conditionals(self, template: str, question_type: QuestionType) -> str:
        """Process question-type specific conditional blocks."""
        # Process data sufficiency blocks
        ds_pattern = r'{{#if_data_sufficiency}}(.*?){{/if_data_sufficiency}}'
        if question_type == QuestionType.DATA_SUFFICIENCY:
            template = re.sub(ds_pattern, r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(ds_pattern, '', template, flags=re.DOTALL)
        
        # Process multiple choice blocks
        mc_pattern = r'{{#if_multiple_choice}}(.*?){{/if_multiple_choice}}'
        if question_type in [QuestionType.PROBLEM_SOLVING, QuestionType.CRITICAL_REASONING]:
            template = re.sub(mc_pattern, r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(mc_pattern, '', template, flags=re.DOTALL)
        
        # Process parent-child blocks
        pc_pattern = r'{{#if_parent_child}}(.*?){{/if_parent_child}}'
        if question_type == QuestionType.READING_COMPREHENSION:
            template = re.sub(pc_pattern, r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(pc_pattern, '', template, flags=re.DOTALL)
        
        return template
    
    def _process_template_inheritance(self, template: str) -> str:
        """Process template inheritance, such as {{GENERIC_PHILOSOPHY_TEMPLATE}}."""
        # Define inheritance patterns to handle
        inheritance_patterns = [
            "{{GENERIC_PHILOSOPHY_TEMPLATE}}",
            "{{0_GENERIC_PHILOSOPHY_TEMPLATE}}"
        ]
        
        # Check if the template contains any generic philosophy template placeholder
        for pattern in inheritance_patterns:
            if pattern in template:
                try:
                    # Load the generic template
                    generic_template_path = Path("system_instructions") / "templates" / "!Main Instructions" / "0_generic.txt.template"
                    if generic_template_path.exists():
                        with open(generic_template_path, 'r', encoding='utf-8') as f:
                            generic_content = f.read()
                        
                        # Replace the placeholder with the generic content
                        template = template.replace(pattern, generic_content)
                    else:
                        # Remove the placeholder if generic template doesn't exist
                        template = template.replace(pattern, "")
                except Exception:
                    # If loading fails, remove the placeholder
                    template = template.replace(pattern, "")
        
        return template
    
    def _apply_variables(self, template: str, variables: Dict[str, str]) -> str:
        """Apply variable substitution to template."""
        try:
            template_obj = Template(template)
            return template_obj.safe_substitute(variables)
        except Exception as e:
            # Fallback to manual replacement for complex cases
            return self._manual_variable_replacement(template, variables)
    
    def _manual_variable_replacement(self, template: str, variables: Dict[str, str]) -> str:
        """Manual variable replacement as fallback."""
        result = template
        for key, value in variables.items():
            # Handle both ${var} and $var patterns
            result = result.replace(f"${{{key}}}", str(value))
            result = result.replace(f"${key}", str(value))
        return result
    
    def _post_process(
        self,
        template: str,
        exam_type: ExamType,
        question_type: QuestionType
    ) -> str:
        """Post-process the template after variable substitution."""
        # Clean up any remaining template artifacts
        template = re.sub(r'{{[^}]*}}', '', template)
        
        # Normalize whitespace
        template = re.sub(r'\\n\\s*\\n\\s*\\n', '\\n\\n', template)
        template = re.sub(r'\\s+$', '', template, flags=re.MULTILINE)
        
        # Ensure proper formatting for specific question types
        if question_type == QuestionType.DATA_SUFFICIENCY:
            template = self._ensure_data_sufficiency_format(template)
        
        return template.strip()
    
    def _get_question_type_display(self, question_type: QuestionType) -> str:
        """Get human-readable question type display name."""
        display_names = {
            QuestionType.DATA_SUFFICIENCY: "Data Sufficiency",
            QuestionType.PROBLEM_SOLVING: "Problem Solving",
            QuestionType.READING_COMPREHENSION: "Reading Comprehension",
            QuestionType.CRITICAL_REASONING: "Critical Reasoning",
            QuestionType.SENTENCE_CORRECTION: "Sentence Correction",
            QuestionType.TEXT_COMPLETION: "Text Completion",
            QuestionType.SENTENCE_EQUIVALENCE: "Sentence Equivalence",
            QuestionType.NUMERIC_ENTRY: "Numeric Entry",
            QuestionType.QUANTITATIVE_COMPARISON: "Quantitative Comparison",
            QuestionType.GRAPHIC_INTERPRETATION: "Graphic Interpretation",
            QuestionType.TABLE_ANALYSIS: "Table Analysis",
            QuestionType.TWO_PART_ANALYSIS: "Two-Part Analysis",
            QuestionType.MULTI_SOURCE_REASONING: "Multi-Source Reasoning"
        }
        return display_names.get(question_type, question_type.value.replace('_', ' ').title())
    
    def _get_difficulty_variables(self, exam_type: ExamType) -> Dict[str, str]:
        """Get difficulty-related template variables."""
        return {
            "DIFFICULTY_RANGE": "1 to 5",
            "DIFFICULTY_DESCRIPTION": f"difficulty level 1 should also be a challenging question which satisfies the {exam_type.value.upper()} standards",
            "DIFFICULTY_SCALING": "higher the difficulty level is, much more difficulty level of logical reasoning should get"
        }
    
    def _get_question_specific_variables(self, question_type: QuestionType) -> Dict[str, str]:
        """Get question-type specific template variables."""
        variables = {}
        
        if question_type == QuestionType.DATA_SUFFICIENCY:
            variables["STANDARD_OPTIONS"] = self.DEFAULT_VARIABLES["DATA_SUFFICIENCY_OPTIONS"]
        
        if question_type in [QuestionType.READING_COMPREHENSION, QuestionType.CRITICAL_REASONING]:
            variables["PASSAGE_REQUIREMENT"] = "Generate a high-quality passage that matches the standards expected in the exam"
        
        if question_type in [QuestionType.GRAPHIC_INTERPRETATION, QuestionType.TABLE_ANALYSIS]:
            variables["VISUAL_ELEMENT_REQUIREMENT"] = "Generate appropriate visual elements (graphs, tables) that support the question"
        
        return variables
    
    def _ensure_data_sufficiency_format(self, template: str) -> str:
        """Ensure proper formatting for data sufficiency questions."""
        # Ensure standard options are included
        if "Statement (1) ALONE is sufficient" not in template:
            template += f"\\n\\n{self.DEFAULT_VARIABLES['DATA_SUFFICIENCY_OPTIONS']}"
        
        return template
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get processor system information.
        
        Returns:
            Dictionary containing processor status and capabilities
        """
        return {
            "default_variables": len(self.DEFAULT_VARIABLES),
            "conditional_patterns": ["if_gmat", "if_gre", "if_data_sufficiency", "if_multiple_choice", "if_parent_child"],
            "variable_patterns": ["${var}", "$var"],
            "post_processing_enabled": True,
            "graph_style_manager": self._graph_style_manager.get_system_info()
        }


class TemplateProcessingError(Exception):
    """Raised when template processing fails."""
    pass