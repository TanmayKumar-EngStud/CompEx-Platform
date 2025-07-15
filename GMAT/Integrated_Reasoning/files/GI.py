import random
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class Generate_GI(BaseQuestionGenerator):
    """GMAT Graphic Interpretation Question Generator using unified architecture."""

    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.GRAPHIC_INTERPRETATION,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )

    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Graphic Interpretation question.

        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)

            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.GRAPHIC_INTERPRETATION,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            gi = GMATAdapter.adapt_graphic_interpretation(
                self.prompt, component)

            # Generate question content
            self.question_data["content"] = gi.generate_questionGraph()
            self.question_data["question"] = gi.generate_questionText()
            self.question_data["title"] = gi.generate_questionTitle()
            self.question_data["solution"] = gi.generate_questionSolution()

            # Generate options and answers
            options_list, correct_option = gi.generate_questionOptions()
            if options_list and correct_option:
                # GI uses TC-2 format: options is array of dicts, answer is array of letters
                if isinstance(options_list, list) and isinstance(correct_option, list):
                    # TC-2 format: options=[{A:..., B:..., C:...}, {D:..., E:..., F:...}], answer=["A", "F"]
                    answer_list = []
                    options = []
                    for i, option_dict in enumerate(options_list):
                        if i < len(correct_option) and isinstance(option_dict, dict):
                            # Add the correct answer for this blank
                            answer_list.append(correct_option[i])
                            # Convert option dict to list of values and shuffle
                            opts = list(option_dict.values())
                            random.shuffle(opts)
                            options.append(opts)
                    
                    self.question_data["options"] = options
                    self.question_data["answer"] = answer_list
                else:
                    # Fallback for unexpected formats
                    self.question_data["options"] = [["Option A", "Option B"]]
                    self.question_data["answer"] = ["Option A"]
            else:
                self.question_data["options"] = [["Option A", "Option B"]]
                self.question_data["answer"] = ["Option A"]

            return self.question_data

        except Exception as e:
            print(
                f"Error generating GMAT Graphic Interpretation question: {e}")
            return None

    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Graphic Interpretation question format.

        Args:
            question_data: Generated question data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content",
                           "question", "answer", "solution", "options"]

        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False

        # Validate options structure
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) == 0:
            return False

        # Validate answer structure
        answer = question_data.get("answer", [])
        if not isinstance(answer, list) or len(answer) == 0:
            return False

        return True

    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.GRAPHIC_INTERPRETATION]

    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT
