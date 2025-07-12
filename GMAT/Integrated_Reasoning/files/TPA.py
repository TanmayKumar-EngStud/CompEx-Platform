# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter
import random
import json
import os
import re
from typing import Dict, Any, Optional


class Generate_TPA(BaseQuestionGenerator):
    """GMAT Two-Part Analysis Question Generator using unified architecture."""

    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.TWO_PART_ANALYSIS,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )

    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Two-Part Analysis question.

        Args:
            prompt: Optional prompt override

        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)

            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.TWO_PART_ANALYSIS,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            tpa = GMATAdapter.adapt_two_part_analysis(self.prompt, component)

            # Generate parent question content
            parentQuestionContent = tpa.generate_ParentQuestionContent()
            self.question_data["content"] = [parentQuestionContent]

            # Prepare difficulty for child questions
            difficulty = self.extract_difficulty_from_prompt()
            d1 = max(1, min(5, difficulty + random.randint(-1, 1)))
            d2 = max(1, min(5, difficulty + random.randint(-1, 1)))

            # Generate child questions
            questions = tpa.generate_QuestionText([d1, d2])
            if not questions or len(questions) < 2:
                print(
                    "Error: Failed to generate questions or insufficient questions returned")
                return None

            solutions = tpa.generate_QuestionSolution()
            if not solutions or len(solutions) < 2:
                print(
                    "Error: Failed to generate solutions or insufficient solutions returned")
                return None

            common_options, answers = tpa.generate_QuestionOptions()
            if not common_options or not answers:
                print("Error: Failed to generate options or answers")
                return None

            try:
                ans1 = common_options[answers["question1"]]
                ans2 = common_options[answers["question2"]]
            except (KeyError, TypeError) as e:
                print(f"Error: Invalid options or answers structure: {e}")
                return None

            title = tpa.generate_QuestionTitle()
            self.question_data["title"] = title or "Two Part Analysis Question"

            option_list = list(common_options.values())
            random.shuffle(option_list)

            # Create child question objects
            q1 = {
                "type": "TPA",
                "question": questions[0],
                "solution": solutions[0],
                "answer": ans1,
                "title": title,
                "prompt": self.prompt,
                "options": option_list,
                "difficulty": d1,
                "tags": self.extract_tags_from_prompt()
            }

            q2 = {
                "type": "TPA",
                "question": questions[1],
                "solution": solutions[1],
                "answer": ans2,
                "title": title,
                "prompt": self.prompt,
                "options": option_list,
                "difficulty": d2,
                "tags": self.extract_tags_from_prompt()
            }

            self.question_data["questions"] = [q1, q2]

            return self.question_data

        except Exception as e:
            print(f"Error generating GMAT Two-Part Analysis question: {e}")
            return None

    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Two-Part Analysis question format.

        Args:
            question_data: Generated question data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content", "questions"]

        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False

        # Validate questions array
        questions = question_data.get("questions", [])
        if not isinstance(questions, list) or len(questions) != 2:
            return False

        # Validate each child question
        for question in questions:
            if not isinstance(question, dict):
                return False
            required_question_fields = [
                "type", "question", "options", "answer"]
            for field in required_question_fields:
                if field not in question:
                    return False

        return True

    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.TWO_PART_ANALYSIS]

    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT
