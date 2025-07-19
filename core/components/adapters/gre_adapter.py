"""
GRE-Specific Adapter

This adapter handles GRE-specific behaviors and adaptations for the unified
question components, ensuring backward compatibility with existing GRE
question generators.

Author: Claude Code (Migration CHUNK 2)
Date: 2025-06-25
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
# REMOVED: unused imports for TC logging
# import json
# import os
# from datetime import datetime
from core.components.question_components import (
    SimpleQuestion,
    DataSufficiencyQuestion,
    ParentChildQuestion
)
from core.template import (
    QuestionMetadata,
    QuestionText,
    QuestionTitle,
    QuestionSolution,
    QuestionOptions,
    QuestionAnswer
)
from core.components.adapters.debug_decorator import debug_log_method


class GREAdapter:
    """
    Adapter class for GRE-specific question generation behaviors.

    This adapter ensures that the unified question components behave exactly
    like the original GRE question generators, maintaining backward compatibility.
    """

    def __init__(self):
        """Initialize GRE adapter."""
        self.exam_type = ExamType.GRE
        self.question_metadata = QuestionMetadata()
        self.question_text = QuestionText()
        self.question_title = QuestionTitle()
        self.question_solution = QuestionSolution()
        self.question_options = QuestionOptions()
        self.question_answer = QuestionAnswer()

    def _is_text_completion_question_from_prompt(self, prompt: str) -> bool:
        """Check if this is a Text Completion question from prompt."""
        prompt_lower = prompt.lower()
        return any(tc_type in prompt_lower for tc_type in ['<tc-1>', '<tc-2>', '<tc-3>', 'tc-1', 'tc-2', 'tc-3'])

    def _is_sentence_equivalence_question_from_prompt(self, prompt: str) -> bool:
        """Check if this is a Sentence Equivalence question from prompt."""
        prompt_lower = prompt.lower()
        return '<se>' in prompt_lower

    @staticmethod
    def adapt_simple_question(prompt: str, component: SimpleQuestion) -> 'GRESimpleQuestionAdapter':
        """Adapt SimpleQuestion for GRE-specific behavior."""
        return GRESimpleQuestionAdapter(prompt, component)

    @staticmethod
    def adapt_data_sufficiency_question(prompt: str, component: DataSufficiencyQuestion) -> 'GREDataSufficiencyAdapter':
        """Adapt DataSufficiencyQuestion for GRE-specific behavior."""
        return GREDataSufficiencyAdapter(prompt, component)

    @staticmethod
    def adapt_parent_child_question(prompt: str, component: ParentChildQuestion) -> 'GREParentChildAdapter':
        """Adapt ParentChildQuestion for GRE-specific behavior."""
        return GREParentChildAdapter(prompt, component)

    def get_metadata_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate metadata template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed metadata template
        """
        if question_type == QuestionType.READING_COMPREHENSION:
            return self.question_metadata.passage(
                self.exam_type, question_type, customizations, prompt
            )
        elif "parent" in prompt.lower() and "quant" in prompt.lower():
            return self.question_metadata.graph(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.QUANTITATIVE_COMPARISON:
            return self.question_metadata.graph(
                self.exam_type, question_type, customizations, prompt
            )
        elif "parent" in prompt.lower() or "child" in prompt.lower():
            return self.question_metadata.parent_stimulus(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            # For other question types, check prompt for special content types
            if "graph" in prompt.lower():
                return self.question_metadata.graph(
                    self.exam_type, question_type, customizations, prompt
                )
            elif "table" in prompt.lower():
                return self.question_metadata.table(
                    self.exam_type, question_type, customizations, prompt
                )
            else:
                # Default to passage template for generic cases
                print(f"no template found for {prompt}")
                return self.question_metadata.passage(
                    self.exam_type, question_type, customizations, prompt
                )

    def get_text_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate text template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed text template
        """
        # Debug logging for Text Completion questions
        if self._is_text_completion_question_from_prompt(prompt):
            print(
                f"DEBUG: get_text_template called with question_type={question_type}, prompt={prompt}")

        # Debug logging for Sentence Equivalence questions
        if self._is_sentence_equivalence_question_from_prompt(prompt):
            print(
                f"DEBUG: get_text_template called with question_type={question_type}, prompt={prompt}")

        if question_type == QuestionType.NUMERIC_ENTRY:
            return self.question_text.numeric_entry(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.TEXT_COMPLETION:
            return self.question_text.text_completion(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.SENTENCE_EQUIVALENCE:
            return self.question_text.sentence_equivalence(
                self.exam_type, question_type, customizations, prompt
            )
        elif "child" in prompt.lower():
            return self.question_text.child_question(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_text.generic(
                self.exam_type, question_type, customizations, prompt
            )

    def get_title_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate text template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed text template
        """

        return self.question_title.generic(
            self.exam_type, question_type, customizations, prompt
        )

    def get_solution_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate solution template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed solution template
        """
        return self.question_solution.generic(
            self.exam_type, question_type, customizations, prompt
        )

    def get_options_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate options template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed options template
        """
        if question_type == QuestionType.SENTENCE_EQUIVALENCE:
            return self.question_options.sentence_equivalence(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.TEXT_COMPLETION:
            return self.question_options.text_completion(
                self.exam_type, question_type, customizations, prompt
            )
        elif "true" in prompt.lower() or "false" in prompt.lower():
            return self.question_options.dichotomous_choice(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_options.generic(
                self.exam_type, question_type, customizations, prompt
            )

    def get_answer_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate answer template for GRE questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed answer template
        """
        # GRE questions typically don't use separate answer templates
        # Parameters are included for interface compatibility
        return ""


class GRESimpleQuestionAdapter:
    """GRE-specific adapter for SimpleQuestion components."""

    def __init__(self, prompt: str, component: SimpleQuestion):
        """Initialize with SimpleQuestion component."""
        self.component = component
        self.prompt = prompt
        self.question_type = self._infer_question_type(prompt)

    def _infer_question_type(self, prompt: str) -> QuestionType:
        """Infer question type from prompt."""
        prompt_lower = prompt.lower()

        # Check for SE (Sentence Equivalence) questions
        if "<se>" in prompt_lower:
            return QuestionType.SENTENCE_EQUIVALENCE

        # Check for TC (Text Completion) questions
        if any(tc_type in prompt_lower for tc_type in ["<tc-1>", "<tc-2>", "<tc-3>"]):
            return QuestionType.TEXT_COMPLETION

        # Default to PROBLEM_SOLVING for other questions
        return QuestionType.PROBLEM_SOLVING

    def generate_questionText(self) -> Optional[str]:
        """Generate question text (GRE naming convention)."""
        # Extract question style from prompt
        question_style = self._extract_question_style(self.prompt)

        component_structure = self.component._get_component_instruction(
            'QuestionText', question_style)
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionText\n{component_structure}"

        # REMOVED: TC logging - we're now focusing on SE only
        # if self._is_text_completion_question():
        #     self._log_tc_instruction(instruction_prompt, "QuestionText")

        return self.component.generate_question_text(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.PROBLEM_SOLVING)
    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionTitle\n{component_structure}"
        return self.component.generate_question_title(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.PROBLEM_SOLVING)
    def generate_questionSolution(self, isNE: bool = False) -> Union[str, Tuple[str, float]]:
        """
        Generate question solution (GRE naming convention).

        Args:
            isNE: Whether this is a numeric entry question

        Returns:
            Solution string for regular questions, or (solution, answer) tuple for NE
        """
        component_structure = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionSolution\n{component_structure}"
        component_structure2 = self.component._get_component_instruction(
            'QuestionAnswer')
        instruction_prompt2 = f"Prompt: {self.prompt}\nMode: QuestionAnswer\n{component_structure2}"
        # supposed to work fine for NE types as well
        return self.component.generate_question_solution(instruction_prompt, instruction_prompt2, is_numeric_entry=isNE)

    @debug_log_method(ExamType.GRE, QuestionType.PROBLEM_SOLVING)
    def generate_questionOptions(self, num_options: Optional[int] = None) -> Tuple[Dict[str, str], str]:
        """Generate question options (GRE naming convention)."""
        # The base component doesn't use num_options parameter, but we accept it for compatibility
        _ = num_options  # Explicitly mark as unused
        # Extract question style from prompt
        question_style = self._extract_question_style(self.prompt)

        component_structure = self.component._get_component_instruction(
            'QuestionOptions', question_style)
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionOptions\n{component_structure}"

        # REMOVED: TC logging - we're now focusing on SE only
        # if self._is_text_completion_question():
        #     self._log_tc_instruction(instruction_prompt, "QuestionOptions")

        return self.component.generate_question_options(instruction_prompt)

    def _extract_question_style(self, prompt: str) -> str:
        """Extract question style from prompt."""
        prompt_lower = prompt.lower()

        # Define style mappings
        style_patterns = [
            ("TC-1", ["<tc-1>", "tc-1"]),
            ("TC-2", ["<tc-2>", "tc-2"]),
            ("TC-3", ["<tc-3>", "tc-3"]),
            ("SE", ["<se>"])
        ]

        for style, patterns in style_patterns:
            if any(pattern in prompt_lower for pattern in patterns):
                return style

        return None  # Use default template

    def _is_text_completion_question(self) -> bool:
        """Check if this is a Text Completion question."""
        prompt_lower = self.prompt.lower()
        return any(tc_type in prompt_lower for tc_type in ['<tc-1>', '<tc-2>', '<tc-3>', 'tc-1', 'tc-2', 'tc-3'])

    # REMOVED: TC logging method - we're now focusing on SE only
    # def _log_tc_instruction(self, instruction_prompt: str, mode: str):
    #     """Log Text Completion instruction prompt for debugging."""

    def _is_text_completion_question_from_prompt(self, prompt: str) -> bool:
        """Check if this is a Text Completion question from prompt."""
        prompt_lower = prompt.lower()
        return any(tc_type in prompt_lower for tc_type in ['<tc-1>', '<tc-2>', '<tc-3>', 'tc-1', 'tc-2', 'tc-3'])


class GREDataSufficiencyAdapter:
    """GRE-specific adapter for DataSufficiencyQuestion components."""

    def __init__(self, prompt: str, component: DataSufficiencyQuestion):
        """Initialize with DataSufficiencyQuestion component."""
        self.component = component
        self.prompt = prompt

    @debug_log_method(ExamType.GRE, QuestionType.DATA_SUFFICIENCY)
    def generate_questionText(self) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """Generate question text components (GRE format: passage, statements, question)."""
        component_structure = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionText\n{component_structure}"
        return self.component.generate_question_text(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.DATA_SUFFICIENCY)
    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionTitle\n{component_structure}"
        return self.component.generate_question_title(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.DATA_SUFFICIENCY)
    def generate_questionSolution(self) -> Tuple[Optional[str], Optional[str]]:
        """Generate question solution and answer (GRE naming convention)."""
        # Get solution
        solution_structure = self.component._get_component_instruction(
            'QuestionSolution')
        solution_prompt = f"Prompt: {self.prompt}\nMode: QuestionSolution\n{solution_structure}"
        solution = self.component.generate_question_solution(solution_prompt)

        # Get answer separately using options method
        answer_structure = self.component._get_component_instruction(
            'QuestionOptions')
        answer_prompt = f"Prompt: {self.prompt}\nMode: QuestionOptions\n{answer_structure}"
        _, answer = self.component.generate_question_options_with_answer(
            answer_prompt)

        return solution, answer

    @debug_log_method(ExamType.GRE, QuestionType.DATA_SUFFICIENCY)
    def generate_questionOptions(self) -> Tuple[List[str], str]:
        """Generate question options (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionOptions\n{component_structure}"
        return self.component.generate_question_options(instruction_prompt)


class GREParentChildAdapter:
    """GRE-specific adapter for ParentChildQuestion components."""

    def __init__(self, prompt: str, component: ParentChildQuestion):
        """Initialize with ParentChildQuestion component."""
        self.prompt = prompt
        self.component = component
        self.child_prompt = None

    @debug_log_method(ExamType.GRE, QuestionType.PROBLEM_SOLVING)
    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph/table (for GRE Quants parent-child questions)."""
        component_structure = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionGraph\n{component_structure}"
        return self.component.generate_question_metadata(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_parentTitle(self) -> Optional[str]:
        """Generate parent title (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: ParentTitle\n{component_structure}"
        return self.component.generate_parent_title(instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_childQuestionTitle(self, index: int) -> Optional[str]:
        """Generate child question title (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionTitle')
        if self.child_prompt is None:
            raise ValueError(
                "child_prompt is not set because generate_childQuestionTitle is called before generate_childQuestion")
        instruction_prompt = f"Main Prompt: {self.prompt}\n Current Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionTitle\n{component_structure}"
        return self.component.generate_child_question_title(index, instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_childQuestion(self, index: int, child_prompt: str) -> Optional[str]:
        """Generate child question text (GRE naming convention)."""
        self.child_prompt = child_prompt
        component_structure = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Current Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionText\n{component_structure}"
        return self.component.generate_child_question(index, instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_childOptions(self, index: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate child question options (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Current Active Child Prompt: {self.child_prompt}\nMode: ChildOptions\n{component_structure}"
        return self.component.generate_child_options(index, instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_childSolution(self, index: int) -> Optional[str]:
        """Generate child question solution (GRE naming convention)."""
        component_structure = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Current Active Child Prompt: {self.child_prompt}\nMode: ChildSolution\n{component_structure}"
        return self.component.generate_child_solution(index, instruction_prompt)

    @debug_log_method(ExamType.GRE, QuestionType.READING_COMPREHENSION)
    def generate_parentQuestionPassage(self, idx: int = 1) -> List[str]:  # ✅
        """Generate question passage/argument for Critical Reasoning [Not for Reading Comprehension](GMAT naming convention).
            Args:
                idx: total number of paragraphs that passage should have
            Returns **passages** as list of string (all the paragraphs)
        """
        component_template = self.component._get_component_instruction(
            "QuestionPassage")
        total_passage = []
        for i in range(idx):
            instruction_prompt = f"{self.prompt}\nmode:- QuestionPassage; generate paragraph {i+1} of {idx}: \n{component_template}"
            metadata = self.component.generate_question_metadata(
                instruction_prompt, i=i + 1, total=idx)
            passage_text = ""
            if metadata and isinstance(metadata, dict) and metadata.get("passage"):
                passage_text = metadata["passage"]
            elif isinstance(metadata, str):  # Fallback for string response
                passage_text = metadata
            total_passage.append(passage_text)
        return total_passage
