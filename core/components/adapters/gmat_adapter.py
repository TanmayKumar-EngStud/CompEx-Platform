"""
GMAT-Specific Adapter

This adapter handles GMAT-specific behaviors and adaptations for the unified
question components, ensuring backward compatibility with existing GMAT
question generators.

Author: Claude Code (Migration CHUNK 2)
Date: 2025-06-25
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import (
    BaseQuestionComponent,
    SimpleQuestion,
    DataSufficiencyQuestion,
    ParentChildQuestion,
    GraphicInterpretationQuestion,
    TableAnalysisQuestion,
    TwoPartAnalysisQuestion,
    MultiSourceReasoningQuestion
)
from core.template import (
    QuestionMetadata,
    QuestionText,
    QuestionTitle,
    QuestionSolution,
    QuestionOptions,
    QuestionAnswer
)


class GMATAdapter:
    """
    Adapter class for GMAT-specific question generation behaviors.

    This adapter ensures that the unified question components behave exactly
    like the original GMAT question generators, maintaining backward compatibility.
    """

    def __init__(self):
        """Initialize GMAT adapter."""
        self.exam_type = ExamType.GMAT
        self.question_metadata = QuestionMetadata()
        self.question_text = QuestionText()
        self.question_title = QuestionTitle()
        self.question_solution = QuestionSolution()
        self.question_options = QuestionOptions()
        self.question_answer = QuestionAnswer()

    @staticmethod
    def adapt_simple_question(component: SimpleQuestion) -> 'GMATSimpleQuestionAdapter':
        """Adapt SimpleQuestion for GMAT-specific behavior."""
        return GMATSimpleQuestionAdapter(component)

    @staticmethod
    def adapt_data_sufficiency_question(component: DataSufficiencyQuestion) -> 'GMATDataSufficiencyAdapter':
        """Adapt DataSufficiencyQuestion for GMAT-specific behavior."""
        return GMATDataSufficiencyAdapter(component)

    @staticmethod
    def adapt_parent_child_question(component: ParentChildQuestion) -> 'GMATParentChildAdapter':
        """Adapt ParentChildQuestion for GMAT-specific behavior."""
        return GMATParentChildAdapter(component)

    @staticmethod
    def adapt_graphic_interpretation(component: GraphicInterpretationQuestion) -> 'GMATGraphicInterpretationAdapter':
        """Adapt GraphicInterpretationQuestion for GMAT-specific behavior."""
        return GMATGraphicInterpretationAdapter(component)

    @staticmethod
    def adapt_table_analysis(component: TableAnalysisQuestion) -> 'GMATTableAnalysisAdapter':
        """Adapt TableAnalysisQuestion for GMAT-specific behavior."""
        return GMATTableAnalysisAdapter(component)

    @staticmethod
    def adapt_two_part_analysis(component: TwoPartAnalysisQuestion) -> 'GMATTwoPartAnalysisAdapter':
        """Adapt TwoPartAnalysisQuestion for GMAT-specific behavior."""
        return GMATTwoPartAnalysisAdapter(component)

    @staticmethod
    def adapt_multi_source_reasoning(component: MultiSourceReasoningQuestion) -> 'GMATMultiSourceReasoningAdapter':
        """Adapt MultiSourceReasoningQuestion for GMAT-specific behavior."""
        return GMATMultiSourceReasoningAdapter(component)

    def get_metadata_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate metadata template for GMAT questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed metadata template
        """
        if question_type == QuestionType.MULTI_SOURCE_REASONING:
            return self.question_metadata.multi_source(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.GRAPHIC_INTERPRETATION:
            return self.question_metadata.graph(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.TABLE_ANALYSIS:
            return self.question_metadata.specialized_table(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.READING_COMPREHENSION:
            return self.question_metadata.passage(
                self.exam_type, question_type, customizations, prompt
            )
        elif "parent" in prompt.lower() or "child" in prompt.lower():
            return self.question_metadata.parent_stimulus(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_metadata.generic(
                self.exam_type, question_type, customizations, prompt
            )

    def get_text_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate text template for GMAT questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed text template
        """
        if question_type == QuestionType.DATA_SUFFICIENCY:
            return self.question_text.data_sufficiency(
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

    def get_solution_template(
        self,
        question_type: QuestionType,
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate solution template for GMAT questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed solution template
        """
        if question_type == QuestionType.DATA_SUFFICIENCY:
            return self.question_solution.data_sufficiency(
                self.exam_type, question_type, customizations, prompt
            )
        else:
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
        Get appropriate options template for GMAT questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed options template
        """
        if "true" in prompt.lower() or "false" in prompt.lower():
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
        Get appropriate answer template for GMAT questions.

        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations

        Returns:
            Processed answer template
        """
        if question_type == QuestionType.DATA_SUFFICIENCY:
            return self.question_answer.data_sufficiency(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            # Most GMAT questions don't use separate answer templates
            return ""


class GMATSimpleQuestionAdapter:
    """GMAT-specific adapter for SimpleQuestion components."""

    def __init__(self, component: SimpleQuestion):
        """Initialize with SimpleQuestion component."""
        self.component = component

    def generate_QuestionPassage(self) -> str:
        """Generate question passage/argument for Critical Reasoning (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionPassage")
        # idx =
        prompt = f"{self.component.prompt}"
        return self.component.generate_question_passage()

    # ✅
    def generate_questionText(self, input_data: Optional[str] = None) -> str:
        """Generate question text (GMAT naming convention)."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionText")
        prompt = input_data if input_data else "QuestionText"
        instruction_prompt = f"{prompt}\n\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_questionTitle(self) -> str:  # ✅
        """Generate question title (GMAT naming convention)."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionTitle")
        instruction_prompt = f"QuestionTitle\n\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_questionSolution(self) -> str:  # ✅
        """Generate question solution (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionSolution")
        instruction_prompt = f"QuestionSolution\n\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt, is_numeric_entry=False)

    def generate_questionOptions(self) -> Tuple[List[str], str]:  # ✅
        """Generate question options (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionOptions")
        instruction_prompt = f"QuestionOptions\n\n{component_template}"
        return self.component.generate_question_options(component_template)


class GMATDataSufficiencyAdapter:
    """GMAT-specific adapter for DataSufficiencyQuestion components."""

    def __init__(self, component: DataSufficiencyQuestion):
        """Initialize with DataSufficiencyQuestion component."""
        self.component = component

    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph/table."""
        return self.component.generate_question_graph()

    def generate_questionText(self) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """Generate question text components."""
        return self.component.generate_question_text()

    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title."""
        return self.component.generate_question_title()

    def generate_questionSolution(self) -> str:
        """Generate question solution only (plain text)."""
        return self.component.generate_question_solution()

    def generate_questionOptions(self) -> Tuple[Dict[str, str], str]:
        """Generate question options and answer."""
        return self.component.generate_question_options_with_answer()


class GMATParentChildAdapter:
    """GMAT-specific adapter for ParentChildQuestion components (Verbal RC)."""

    def __init__(self, component: ParentChildQuestion):
        """Initialize with ParentChildQuestion component."""
        self.component = component

    def generate_parentTitle(self) -> Optional[str]:
        """Generate parent title."""
        return self.component.generate_parent_title()

    def generate_parentQuestion(self) -> Optional[str]:
        """Generate parent question (passage content)."""
        return self.component.generate_parent_question()

    def generate_childQuestionTitle(self, index: int) -> Optional[str]:
        """Generate child question title."""
        return self.component.generate_child_question_title(index)

    def generate_childQuestion(self, index: int, child_prompt: str = "") -> Optional[str]:
        """Generate child question text."""
        return self.component.generate_child_question(index, child_prompt)

    def generate_childOptions(self, index: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate child question options."""
        return self.component.generate_child_options(index)

    def generate_childSolution(self, index: int) -> Optional[str]:
        """Generate child question solution."""
        return self.component.generate_child_solution(index)


class GMATGraphicInterpretationAdapter:
    """GMAT-specific adapter for GraphicInterpretationQuestion components."""

    def __init__(self, component: GraphicInterpretationQuestion):
        """Initialize with GraphicInterpretationQuestion component."""
        self.component = component

    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph."""
        return self.component.generate_question_graph()

    def generate_questionText(self) -> Optional[str]:
        """Generate question text."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionText")
        instruction_prompt = f"Mode: QuestionText return: `question`\n\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionTitle")
        instruction_prompt = f"Mode: QuestionTitle return: `title`\n\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_questionSolution(self) -> Optional[str]:
        """Generate question solution."""
        return self.component.generate_question_solution()

    def generate_questionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options."""
        return self.component.generate_question_options()


class GMATTableAnalysisAdapter:
    """GMAT-specific adapter for TableAnalysisQuestion components."""

    def __init__(self, component: TableAnalysisQuestion):
        """Initialize with TableAnalysisQuestion component."""
        self.component = component

    def generate_QuestionTable(self, no_rows: int, no_cols: int) -> Optional[Dict[str, Any]]:
        """Generate question table (GMAT naming convention)."""
        return self.component.generate_question_table(no_rows, no_cols)

    def generate_QuestionText(self) -> Optional[str]:
        """Generate question text (GMAT naming convention)."""
        return self.component.generate_question_text()

    def generate_QuestionTitle(self) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        return self.component.generate_question_title()

    def generate_QuestionSolution(self) -> Optional[str]:
        """Generate question solution (GMAT naming convention)."""
        return self.component.generate_question_solution()

    def generate_QuestionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options (GMAT naming convention)."""
        return self.component.generate_question_options()


class GMATTwoPartAnalysisAdapter:
    """GMAT-specific adapter for TwoPartAnalysisQuestion components."""

    def __init__(self, component: TwoPartAnalysisQuestion):
        """Initialize with TwoPartAnalysisQuestion component."""
        self.component = component

    def generate_ParentQuestionContent(self) -> Optional[Dict[str, Any]]:
        """Generate parent question content (GMAT naming convention)."""
        return self.component.generate_parent_question_content()

    def generate_QuestionText(self, difficulties: List[int]) -> List[str]:
        """Generate question texts (GMAT naming convention)."""
        return self.component.generate_question_text(difficulties)

    def generate_QuestionTitle(self) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        return self.component.generate_question_title()

    def generate_QuestionSolution(self) -> List[str]:
        """Generate question solutions (GMAT naming convention)."""
        return self.component.generate_question_solution()

    def generate_QuestionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options (GMAT naming convention)."""
        return self.component.generate_question_options()


class GMATMultiSourceReasoningAdapter:
    """GMAT-specific adapter for MultiSourceReasoningQuestion components."""

    def __init__(self, component: MultiSourceReasoningQuestion):
        """Initialize with MultiSourceReasoningQuestion component."""
        self.component = component

    def generate_SourceInfo(self, prompt: str, idx: int) -> Optional[Dict[str, Any]]:
        """Generate source information (GMAT naming convention)."""
        # idx parameter is included for compatibility but not used
        return self.component.generate_source_info(prompt)

    def generate_MainQuestionTitle(self) -> Optional[str]:
        """Generate main question title (GMAT naming convention)."""
        return self.component.generate_main_question_title()

    def generate_QuestionText(self, prompt: str) -> Optional[str]:
        """Generate question text (GMAT naming convention)."""
        return self.component.generate_question_text(prompt)

    def generate_QuestionTitle(self, prompt: str) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        return self.component.generate_question_title(prompt)

    def generate_QuestionSolution(self, prompt: str) -> Optional[str]:
        """Generate question solution (GMAT naming convention)."""
        return self.component.generate_question_solution(prompt)

    def generate_QuestionOptions(self, prompt: str, question_style: str) -> Union[Tuple[Any, Any], Any]:
        """Generate question options (GMAT naming convention)."""
        return self.component.generate_question_options(prompt, question_style)
