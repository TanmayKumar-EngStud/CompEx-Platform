"""
GMAT Integrated Reasoning Prompt Generator.

This module provides prompt generation specifically for GMAT Integrated Reasoning sections,
handling GI, TPA, TA, and MSR question types.
"""

from typing import List
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from ..base.base_prompt_generator import BasePromptGenerator


class GMATIRPrompts(BasePromptGenerator):
    """
    GMAT Integrated Reasoning prompt generator.

    Generates prompts for GMAT IR questions including Graphic Interpretation,
    Two-Part Analysis, Table Analysis, and Multi-Source Reasoning.
    """

    def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
        """Initialize GMAT IR prompt generator."""
        super().__init__(exam_type, section_type, mock_difficulty)

    def _get_total_questions(self) -> int:
        """Get total number of questions for GMAT IR section."""
        return 8  # Base number for mock generation

    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GMAT Integrated Reasoning section using nomenclature patterns.

        Returns:
            nomenclature:
            GI: `GI - <questionTheme> - <focused_skill> - <graphType> - <difficulty_level: {1-5}>`
            MSR: `MSR - <total_child_questions> - <questionTheme> - <source_info1> - <source_info2> - <source_info3> - <focused_skill_1/focused_skill_2/focused_skill_3> - <question_style_1/question_style_2/question_style_3> - <difficulty_level: {1-5}>`
            TA: `TA - <focused_skill> - <tableType> - <dichotomousType> - <questionTheme> - <difficulty_level: {1-5}>`
            TPA: `TPA - <questionTheme> - <focused_skill> - <type> - <difficulty_level: {1-5}>`
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []

        # Get question distribution from customizations
        section_config = self.customizations.get("integrated reasoning", {})
        num_msr = section_config.get("Multi_Source_Reasoning", 6)
        num_ta = section_config.get("Table_Analysis", 5)
        num_gi = section_config.get("Graphics_Interpretation", 5)
        num_tpa = section_config.get("Two_Part_Analysis", 4)

        question_index = 0

        # Generate MSR prompts using nomenclature
        for _ in range(num_msr):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "multi source reasoning",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate TA prompts using nomenclature
        for _ in range(num_ta):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "table analysis",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate GI prompts using nomenclature
        for _ in range(num_gi):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "graphic interpretation",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate TPA prompts using nomenclature
        for _ in range(num_tpa):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "two part analysis",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        return prompts

    def _get_default_component_allocation(self):
        """
        Get GMAT Integrated Reasoning specific component allocation.

        Note: This is now primarily loaded from customizations.json file.
        These are fallback defaults if customizations file is not available.
        """
        return {
            "Multi_Source_Reasoning": 6,
            "Table_Analysis": 5,
            "Graphics_Interpretation": 5,
            "Two_Part_Analysis": 4
        }
