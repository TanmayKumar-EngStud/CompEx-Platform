"""
QuestionText template class for handling text generation templates.

This class manages question text template loading and processing,
including data sufficiency, numeric entry, and child question formats.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from core.instructions.template_processor import TemplateProcessor


class QuestionText:
    """
    Handles question text template loading and processing.

    This class provides methods for different question text formats,
    handling exam-specific conditional blocks and format requirements.
    """

    def __init__(self):
        """Initialize the QuestionText handler."""
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
        Load generic question text template from 1-questionText/0-generic.txt.template

        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing

        Returns:
            Processed generic question text template
        """
        template = self._load_template_file(
            "1-questionText/0-generic.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )

    def data_sufficiency(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load data sufficiency question text template from 1-questionText/1-data_sufficiency.txt.template

        Handles GMAT data sufficiency question format requirements.

        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing

        Returns:
            Processed data sufficiency question text template
        """
        template = self._load_template_file(
            "1-questionText/1-data_sufficiency.txt.template")

        # Apply data sufficiency specific processing
        processed_template = self._apply_conditional_blocks(
            template, exam_type)

        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def numeric_entry(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load numeric entry question text template from 1-questionText/2-numeric_entry.txt.template

        Handles GRE numeric entry question format requirements.

        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing

        Returns:
            Processed numeric entry question text template
        """
        template = self._load_template_file(
            "1-questionText/2-numeric_entry.txt.template")

        # Apply numeric entry specific processing
        processed_template = self._apply_conditional_blocks(
            template, exam_type)

        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def child_question(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load child question text template from `1-questionText/3-child_question.txt.template`

        Handles child questions in parent-child question structures.

        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing

        Returns:
            Processed child question text template
        """
        template = self._load_template_file(
            "1-questionText/3-child_question.txt.template")

        # Apply child question specific processing
        processed_template = self._apply_conditional_blocks(
            template, exam_type)

        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def text_completion(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load text completion question text template from 1-questionText/4-text_completion.txt.template
        
        Handles GRE text completion question format with proper fill-in-the-blank styles.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed text completion question text template
        """
        template = self._load_template_file(
            "1-questionText/4-text_completion.txt.template")
        
        # Apply text completion specific processing
        processed_template = self._apply_conditional_blocks(
            template, exam_type)
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def _apply_conditional_blocks(self, template: str, exam_type: ExamType) -> str:
        """
        Apply exam-specific conditional blocks to template.

        Processes {{#if_gmat}}, {{#if_gre}} blocks based on exam type.

        Args:
            template: Raw template content
            exam_type: Target exam type

        Returns:
            Template with conditional blocks processed
        """
        try:
            processed_template = template

            # Process GMAT conditional blocks
            if exam_type == ExamType.GMAT:
                # Keep GMAT content, remove GRE content
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gmat}}", "{{/if_gmat}}", keep=True
                )
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gre}}", "{{/if_gre}}", keep=False
                )
            else:  # GRE
                # Keep GRE content, remove GMAT content
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gre}}", "{{/if_gre}}", keep=True
                )
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gmat}}", "{{/if_gmat}}", keep=False
                )

            return processed_template
        except Exception as e:
            self._logger.error(f"Failed to apply conditional blocks: {e}")
            return template

    def _apply_se_conditional_blocks(self, template: str, exam_type: ExamType) -> str:
        """
        Apply SE-specific conditional blocks to template.

        Processes {{#if_se}}, {{/if_se}} blocks for sentence equivalence modifications.

        Args:
            template: Raw template content
            exam_type: Target exam type

        Returns:
            Template with SE conditional blocks processed
        """
        try:
            processed_template = template

            # Keep SE content, remove TC content
            processed_template = self._process_conditional_block(
                processed_template, "{{#if_se}}", "{{/if_se}}", keep=True
            )
            
            # Remove TC-specific content that doesn't apply to SE
            processed_template = self._process_conditional_block(
                processed_template, "{{#if_tc}}", "{{/if_tc}}", keep=False
            )

            # Apply standard exam-specific blocks
            if exam_type == ExamType.GMAT:
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gmat}}", "{{/if_gmat}}", keep=True
                )
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gre}}", "{{/if_gre}}", keep=False
                )
            else:  # GRE
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gre}}", "{{/if_gre}}", keep=True
                )
                processed_template = self._process_conditional_block(
                    processed_template, "{{#if_gmat}}", "{{/if_gmat}}", keep=False
                )

            return processed_template

        except Exception as e:
            self._logger.error(f"Failed to apply SE conditional blocks: {e}")
            return template

    def sentence_equivalence(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load sentence equivalence question text template.
        
        SE questions use the same TC-1 template (single blank) but with SE-specific 
        conditional blocks that describe the two-word selection requirement.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed template string with SE-specific modifications
        """
        # Load the text completion template
        template = self._load_template_file(
            "1-questionText/4-text_completion.txt.template")
        
        # Apply SE-specific conditional blocks processing
        processed_template = self._apply_se_conditional_blocks(
            template, exam_type)
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def _process_conditional_block(
        self,
        template: str,
        start_tag: str,
        end_tag: str,
        keep: bool
    ) -> str:
        """
        Process a single conditional block in the template.

        Args:
            template: Template content
            start_tag: Opening conditional tag
            end_tag: Closing conditional tag
            keep: Whether to keep the content inside the block

        Returns:
            Template with conditional block processed
        """
        while start_tag in template and end_tag in template:
            start_index = template.find(start_tag)
            end_index = template.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                break

            # Extract content between tags
            content_start = start_index + len(start_tag)
            content = template[content_start:end_index]

            # Replace the entire block with content or empty string
            replacement = content if keep else ""
            template = (
                template[:start_index] +
                replacement +
                template[end_index + len(end_tag):]
            )

        return template

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
