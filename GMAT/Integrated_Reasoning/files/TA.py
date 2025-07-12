# `<TA> - <focused_skill> - <TableType> - <QuestionType> - <QuestionTheme> - <DifficultyLevel>`

import random
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class Generate_TA(BaseQuestionGenerator):
    """GMAT Table Analysis Question Generator using unified architecture."""

    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.TABLE_ANALYSIS,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )

    # Removed _load_default_system_instructions - now uses unified instruction system from base class
    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Table Analysis question.

        Args:
            prompt: Optional prompt override

        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)

            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.TABLE_ANALYSIS,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            ta = GMATAdapter.adapt_table_analysis(self.prompt, component)

            # Calculate table dimensions based on difficulty
            difficulty = self.extract_difficulty_from_prompt()
            no_rows = difficulty + random.randint(5, 7)
            no_cols = difficulty + random.randint(3, 5)

            # Generate table content
            content = ta.generate_QuestionTable(no_rows, no_cols)
            self.question_data["content"] = {"tables": content}

            # Generate question components
            self.question_data["question"] = ta.generate_QuestionText()
            self.question_data["title"] = ta.generate_QuestionTitle()
            self.question_data["solution"] = ta.generate_QuestionSolution()

            # Generate options and answers
            options, answers = ta.generate_QuestionOptions()
            if options and answers:
                option_list = list(options.values())
                random.shuffle(option_list)
                self.question_data["options"] = option_list
                self.question_data["answer"] = {
                    options[key]: answers[key] for key in options}
            else:
                self.question_data["options"] = ["True", "False"]
                self.question_data["answer"] = {"True": True, "False": False}

            return self.question_data

        except Exception as e:
            print(f"Error generating GMAT Table Analysis question: {e}")
            return None

    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Table Analysis question format.

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

        # Validate content structure
        content = question_data.get("content", {})
        if not isinstance(content, dict) or "tables" not in content:
            return False

        # Validate options
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) == 0:
            return False

        return True

    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.TABLE_ANALYSIS]

    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT
