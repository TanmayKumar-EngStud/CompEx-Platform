"""
GMAT Quantitative Prompt Generator.

This module provides prompt generation specifically for GMAT Quantitative sections,
handling the specific requirements and question types for GMAT math questions.
"""

from typing import List
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from ..base.base_prompt_generator import BasePromptGenerator


class GMATQuantsPrompts(BasePromptGenerator):
    """
    GMAT Quantitative prompt generator.

    Generates prompts for GMAT quantitative questions including Data Sufficiency
    and Problem Solving questions with appropriate topic and skill distributions.
    """

    def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
        """Initialize GMAT Quantitative prompt generator."""
        super().__init__(exam_type, section_type, mock_difficulty)

    def _get_total_questions(self) -> int:
        """Get total number of questions for GMAT Quantitative section."""
        return 21  # Base number for mock generation (will be adjusted with buffer)

    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GMAT Quantitative section using nomenclature patterns.

        Returns:
            nomenclature:
            Data Sufficiency/Problem Solving: `{DS/S} - <questionTopic> - <questionTheme> - <questionStyle> - <graphType/tableType> - <focused_skill> - <difficulty_level: {1-5}>`
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []

        # Get question distribution from customizations
        section_config = self.customizations.get("quants", {})
        num_problem_solving = section_config.get("Problem_Solving", 13)
        num_data_sufficiency = section_config.get("Data_Sufficiency", 8)

        question_index = 0

        # Generate Problem Solving prompts using nomenclature
        for _ in range(num_problem_solving):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for Problem Solving
            prompt = self.generate_nomenclature_based_prompt(
                "problem solving",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate Data Sufficiency prompts using nomenclature
        for _ in range(num_data_sufficiency):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for Data Sufficiency
            prompt = self.generate_nomenclature_based_prompt(
                "data sufficiency",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        return prompts

    def _get_default_component_allocation(self):
        """
        Get GMAT Quantitative specific component allocation.

        Note: This is now primarily loaded from customizations.json file.
        These are fallback defaults if customizations file is not available.
        """
        return {
            "Problem_Solving": 13,
            "Data_Sufficiency": 8,
        }
