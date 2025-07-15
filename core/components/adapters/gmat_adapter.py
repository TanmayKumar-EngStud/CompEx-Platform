"""
GMAT-Specific Adapter

This adapter handles GMAT-specific behaviors and adaptations for the unified
question components, ensuring backward compatibility with existing GMAT
question generators.

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
    def adapt_simple_question(prompt: str, component: SimpleQuestion) -> 'GMATSimpleQuestionAdapter':
        """Adapt SimpleQuestion for GMAT-specific behavior."""
        return GMATSimpleQuestionAdapter(prompt, component)

    @staticmethod
    def adapt_data_sufficiency_question(prompt: str, component: DataSufficiencyQuestion) -> 'GMATDataSufficiencyAdapter':
        """Adapt DataSufficiencyQuestion for GMAT-specific behavior."""
        return GMATDataSufficiencyAdapter(prompt, component)

    @staticmethod
    def adapt_parent_child_question(prompt: str, component: ParentChildQuestion) -> 'GMATParentChildAdapter':
        """Adapt ParentChildQuestion for GMAT-specific behavior."""
        return GMATParentChildAdapter(prompt, component)

    @staticmethod
    def adapt_graphic_interpretation(prompt: str, component: GraphicInterpretationQuestion) -> 'GMATGraphicInterpretationAdapter':
        """Adapt GraphicInterpretationQuestion for GMAT-specific behavior."""
        return GMATGraphicInterpretationAdapter(prompt, component)

    @staticmethod
    def adapt_table_analysis(prompt: str,  component: TableAnalysisQuestion) -> 'GMATTableAnalysisAdapter':
        """Adapt TableAnalysisQuestion for GMAT-specific behavior."""
        return GMATTableAnalysisAdapter(prompt, component)

    @staticmethod
    def adapt_two_part_analysis(prompt: str, component: TwoPartAnalysisQuestion) -> 'GMATTwoPartAnalysisAdapter':
        """Adapt TwoPartAnalysisQuestion for GMAT-specific behavior."""
        return GMATTwoPartAnalysisAdapter(prompt, component)

    @staticmethod
    def adapt_multi_source_reasoning(prompt: str, component: MultiSourceReasoningQuestion) -> 'GMATMultiSourceReasoningAdapter':
        """Adapt MultiSourceReasoningQuestion for GMAT-specific behavior."""
        return GMATMultiSourceReasoningAdapter(prompt, component)

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
            return self.question_metadata.multi_sourceInfo(
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

    def get_title_template(
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
            Processed title template
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
        if "dichotomous" in prompt.lower():
            return self.question_options.dichotomous_choice(
                self.exam_type, question_type, customizations, prompt
            )
        elif "GI" in prompt:
            from core.enums.exam_types import ExamType
            from core.enums.question_types import QuestionType as QType
            return self.question_options.text_completion(
                ExamType.GRE, QType.TEXT_COMPLETION, customizations, "TC-2"+prompt
            )  # mimicking TC-2 format for question_option generation for Graphical Interpretation
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

    def __init__(self, prompt: str, component: SimpleQuestion):  # ✅
        """Initialize with SimpleQuestion component."""
        self.prompt = prompt
        self.component = component

    def generate_QuestionPassage(self, idx: int) -> str:  # ✅
        """Generate question passage/argument for Critical Reasoning [Not for Reading Comprehension](GMAT naming convention).
            Args:
                idx: total number of paragraphs that passage should have
            Returns **passages** as string
        """
        component_template = self.component._get_component_instruction(
            "QuestionPassage")
        total_passage = ""
        for i in range(idx):
            instruction_prompt = f"{self.prompt}\nmode:- QuestionPassage; generate paragraph {i+1} of {idx}: \n{component_template}"
            total_passage += f"{self.component.generate_question_passage(instruction_prompt)}\n"
        return total_passage

    def generate_questionText(self) -> str:  # ✅
        """Generate question text (GMAT naming convention)."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionText")
        instruction_prompt = f"{self.prompt}\nmode:- QuestionText\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_questionTitle(self) -> str:  # ✅
        """Generate question title (GMAT naming convention)."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionTitle")
        instruction_prompt = f"{self.prompt}\nmode:- QuestionTitle\n\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_questionSolution(self) -> str:  # ✅
        """Generate question solution (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionSolution")
        instruction_prompt = f"{self.prompt}\nmode:- QuestionSolution\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt, is_numeric_entry=False)

    def generate_questionOptions(self) -> Tuple[List[str], str]:  # ✅
        """Generate question options (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionOptions")
        instruction_prompt = f"{self.prompt}\nmode:- QuestionOptions\n\n{component_template}"
        return self.component.generate_question_options(instruction_prompt)


class GMATDataSufficiencyAdapter:
    """GMAT-specific adapter for DataSufficiencyQuestion components."""

    def __init__(self, prompt: str, component: DataSufficiencyQuestion):
        """Initialize with DataSufficiencyQuestion component."""
        self.component = component
        self.prompt = prompt

    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph/table."""
        component_template = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"{self.prompt}\nmode:- QuestionGraph\n{component_template}"
        return self.component.generate_question_graph(instruction_prompt)

    def generate_questionText(self) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """Generate question text components."""
        component_template = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"{self.prompt}\nmode:- QuestionText\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title."""
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"{self.prompt}\nmode:- QuestionTitle\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_questionSolution(self) -> str:
        """Generate question solution only (plain text)."""
        component_template = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"{self.prompt}\nmode:- QuestionSolution\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt)

    def generate_questionOptions(self) -> Tuple[Dict[str, str], str]:
        """Generate question options and answer."""
        component_template = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"{self.prompt}\nmode:- QuestionOptions\n{component_template}"
        return self.component.generate_question_options_with_answer(instruction_prompt)


class GMATParentChildAdapter:
    """GMAT-specific adapter for ParentChildQuestion components (Verbal RC)."""

    def __init__(self, prompt: str, component: ParentChildQuestion):
        """Initialize with ParentChildQuestion component."""
        self.prompt = prompt
        self.child_prompt = None
        self.component = component
        self.flow = []

    def generate_parentQuestion(self) -> Optional[str]:
        """Generate parent question passage for reading comprehension (GMAT naming convention)."""
        # For RC questions, we need to generate the passage content
        component_structure = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionPassage\n{component_structure}"
        result = self.component.generate_question_metadata(instruction_prompt, i=1, total=1)
        
        # Extract the passage text from the JSON response
        if result and isinstance(result, dict) and "passage" in result:
            return result["passage"]
        elif result and isinstance(result, str):
            return result
        else:
            return None

    def generate_parentTitle(self) -> Optional[str]:
        """Generate parent title."""
        self.flow.append('ParentTitle')
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"{self.prompt}\n mode: ParentTitle\n{component_template}"
        return self.component.generate_parent_title(instruction_prompt)

    def generate_childQuestionTitle(self, index: int) -> Optional[str]:
        """Generate child question title."""
        self.flow.append('ChildTitle')
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        if self.child_prompt is None:
            raise ValueError(
                f"{self.__class__.__name__}.{self.generate_childTitle.__name__} was called before childQuestion({self.__class__.__name__}.{self.generate_childQuestion.__name__}), thus child_prompt was not saved")
        instruction_prompt = f"{self.child_prompt}\n{component_template}"
        return self.component.generate_child_question_title(index, instruction_prompt)

    def generate_childQuestion(self, index: int, child_prompt: str) -> Optional[str]:
        """Generate child question text."""
        self.flow.append('ChildQuestion')
        self.child_prompt = child_prompt
        component_template = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"Child Prompt: {self.child_prompt}\n{component_template}"
        return self.component.generate_child_question(index, instruction_prompt)

    def generate_childOptions(self, index: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate child question options."""
        component_template = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"Child Prompt: {self.child_prompt}\n {component_template}"
        if self.child_prompt is None:
            raise ValueError(
                f"{self.__class__.__name__}.{self.generate_childOptions.__name__} was called before childQuestion({self.__class__.__name__}.{self.generate_childQuestion.__name__}), thus child_prompt was not saved")
        return self.component.generate_child_options(index, instruction_prompt)

    def generate_childSolution(self, index: int) -> Optional[str]:
        """Generate child question solution."""
        component_template = self.component._get_component_instruction(
            'QuestionSolution')
        if self.child_prompt is None:
            raise ValueError(
                f"{self.__class__.__name__}.{self.generate_childOptions.__name__} was called before childQuestion({self.__class__.__name__}.{self.generate_childQuestion.__name__}), thus child_prompt was not saved")
        instruction_prompt = f"Child Prompt: {self.child_prompt}\n {component_template}"
        return self.component.generate_child_solution(index, instruction_prompt)


class GMATGraphicInterpretationAdapter:
    """GMAT-specific adapter for GraphicInterpretationQuestion components."""

    def __init__(self, prompt: str, component: GraphicInterpretationQuestion):
        """Initialize with GraphicInterpretationQuestion component."""
        self.component = component
        self.prompt = prompt

    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph."""
        component_template = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionGraph\n{component_template}"
        return self.component.generate_question_graph(instruction_prompt)

    def generate_questionText(self) -> Optional[str]:
        """Generate question text."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionText")
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionText\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title."""
        # Get component template and combine with prompt
        component_template = self.component._get_component_instruction(
            "QuestionTitle")
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionTitle\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_questionSolution(self) -> Optional[str]:
        """Generate question solution."""
        component_template = self.component._get_component_instruction(
            "QuestionSolution")
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionSolution\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt)

    def generate_questionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options."""
        component_template = self.component._get_component_instruction(
            "QuestionOptions")
        instruction_prompt = f"{self.prompt}\nMode: QuestionOptions\n{component_template}"
        return self.component.generate_question_options(instruction_prompt)


class GMATTableAnalysisAdapter:
    """GMAT-specific adapter for TableAnalysisQuestion components."""

    def __init__(self, prompt: str, component: TableAnalysisQuestion):
        """Initialize with TableAnalysisQuestion component."""
        self.component = component
        self.prompt = prompt

    def generate_QuestionTable(self, no_rows: int, no_cols: int) -> Optional[Dict[str, Any]]:
        """Generate question table (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"{self.prompt}\n{component_template}"
        return self.component.generate_question_table(instruction_prompt, no_rows, no_cols)

    def generate_QuestionText(self) -> Optional[str]:
        """Generate question text (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"{self.prompt}\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_QuestionTitle(self) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"{self.prompt}\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_QuestionSolution(self) -> Optional[str]:
        """Generate question solution (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"{self.prompt}\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt)

    def generate_QuestionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"{self.prompt}\n{component_template}"
        return self.component.generate_question_options(instruction_prompt)


class GMATTwoPartAnalysisAdapter:
    """GMAT-specific adapter for TwoPartAnalysisQuestion components."""

    def __init__(self, prompt: str, component: TwoPartAnalysisQuestion):
        """Initialize with TwoPartAnalysisQuestion component."""
        self.prompt = prompt
        self.component = component
        self.child_prompt = None

    def generate_ParentQuestionContent(self) -> Optional[Dict[str, Any]]:
        """Generate parent question content (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            "QuestionMetadata")
        instruction_prompt = f"{self.prompt}\nMode: \n{component_template}"
        return self.component.generate_parent_question_content(instruction_prompt)

    def generate_QuestionText(self, difficulties: List[int]) -> List[str]:
        """Generate question texts (GMAT naming convention).
            Args:
                difficulties: list of both the child prompt's difficulties
            Return:
                List of both the child question text
        """
        component_template = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionText\n{component_template}"
        return self.component.generate_question_text(instruction_prompt, difficulties)

    def generate_QuestionTitle(self) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Prompt: {self.prompt}\nMode:- QuestionTitle\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_QuestionSolution(self) -> List[str]:
        """Generate question solutions (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"Prompt: {self.prompt}\nMode: QuestionSolution\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt)

    def generate_QuestionOptions(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate question options (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"{self.prompt}\nMode: QuestionOptions\n{component_template}"
        return self.component.generate_question_options(instruction_prompt)


class GMATMultiSourceReasoningAdapter:
    """GMAT-specific adapter for MultiSourceReasoningQuestion components."""

    def __init__(self, prompt: str, component: MultiSourceReasoningQuestion):
        """Initialize with MultiSourceReasoningQuestion component."""
        self.component = component
        self.prompt = prompt
        self.child_prompt = None
        self.child_idx = 0

    def generate_SourceInfo(self, prompt: str, idx: int) -> Optional[Dict[str, Any]]:
        """Generate source information (GMAT naming convention).
            Args: 
                prompt: prompt of source_info{i}
                idx: source_info index
            Return:
                value for "source" key is to be sent directly
        """
        # idx parameter is included for compatibility but not used
        component_template = self.component._get_component_instruction(
            'QuestionMetadata')
        instruction_prompt = f"Main Prompt:- {self.prompt}\n Mode:- Source_info{idx} Prompt: {prompt}\n{component_template}"
        return self.component.generate_source_info(instruction_prompt, idx)

    def generate_MainQuestionTitle(self) -> Optional[str]:
        """Generate main question title (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Main Prompt:- {self.prompt}\nMode:- MainQuestionTitle\n{component_template}"
        return self.component.generate_main_question_title(instruction_prompt)

    def generate_QuestionText(self, child_prompt: str, idx: int) -> Optional[str]:
        """Generate question text (GMAT naming convention)."""
        self.child_prompt = child_prompt
        self.child_idx = idx
        component_template = self.component._get_component_instruction(
            'QuestionText')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionText of question number: {idx}\n{component_template}"
        return self.component.generate_question_text(instruction_prompt)

    def generate_QuestionTitle(self) -> Optional[str]:
        """Generate question title (GMAT naming convention)."""
        if self.child_prompt is None:
            raise ValueError(
                f"{self.__class__.__name__}.{self.generate_QuestionTitle.__name__} was called before {self.__class__.__name__}.{self.generate_QuestionText.__name__} function, that is why, Child prompt waws not set")
        component_template = self.component._get_component_instruction(
            'QuestionTitle')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionTitle of question number: {self.child_idx}\n{component_template}"
        return self.component.generate_question_title(instruction_prompt)

    def generate_QuestionSolution(self) -> Optional[str]:
        """Generate question solution (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionSolution')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionSolution of question number: {self.child_idx}\n{component_template}"
        return self.component.generate_question_solution(instruction_prompt)

    def generate_QuestionOptions(self, question_style: str) -> Union[Tuple[Any, Any], Any]:
        """Generate question options (GMAT naming convention)."""
        component_template = self.component._get_component_instruction(
            'QuestionOptions')
        instruction_prompt = f"Main Prompt: {self.prompt}\n Active Child Prompt: {self.child_prompt}\nMode: ChildQuestionOptions of question number: {self.child_idx}\n{component_template}"
        return self.component.generate_question_options(instruction_prompt, question_style)
