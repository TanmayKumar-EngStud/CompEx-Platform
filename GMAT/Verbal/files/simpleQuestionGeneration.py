import sys
import os
import json
import re
import random
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class SimpleQuestionGeneration(BaseQuestionGenerator):
    """GMAT Verbal Simple/Critical Reasoning Question Generator using unified architecture."""

    def __init__(self, global_state, lock, api_IDX, prompt=None):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.CRITICAL_REASONING,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt or ""
        )

    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Verbal Critical Reasoning question.

        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)

            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.CRITICAL_REASONING,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            questionContent = GMATAdapter.adapt_simple_question(
                self.prompt, component)

            # Generate content
            passages = questionContent.generate_QuestionPassage()
            self.question_data["content"] = {"passages": passages}

            self.question_data["question"] = questionContent.generate_questionText(
            )
            self.question_data["title"] = questionContent.generate_questionTitle()

            options, answer = questionContent.generate_questionOptions()
            if options and answer in options:
                self.question_data["answer"] = options[answer]
                options_list = list(options.values())
                random.shuffle(options_list)
                self.question_data["options"] = options_list
            else:
                self.question_data["options"] = [
                    "Option A", "Option B", "Option C", "Option D"]
                self.question_data["answer"] = "Option A"

            self.question_data["solution"] = questionContent.generate_questionSolution(
            )

            return self.question_data

        except Exception as e:
            print(f"Error generating GMAT Verbal Simple question: {e}")
            return None

    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Verbal Simple question format.

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
        if not isinstance(content, dict) or "passages" not in content:
            return False

        # Validate options
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) < 2:
            return False

        # Validate answer is in options
        answer = question_data.get("answer", "")
        if answer not in options:
            return False

        return True

    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.CRITICAL_REASONING]

    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT
