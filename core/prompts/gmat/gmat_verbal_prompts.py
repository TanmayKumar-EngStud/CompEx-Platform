"""
GMAT Verbal Prompt Generator.

This module provides prompt generation specifically for GMAT Verbal sections,
handling Reading Comprehension and Critical Reasoning question types.
"""

from typing import List
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from ..base.base_prompt_generator import BasePromptGenerator


class GMATVerbalPrompts(BasePromptGenerator):
    """
    GMAT Verbal prompt generator.

    Generates prompts for GMAT verbal questions including Reading Comprehension
    and Critical Reasoning with appropriate theme and skill distributions.
    """

    def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
        """Initialize GMAT Verbal prompt generator."""
        super().__init__(exam_type, section_type, mock_difficulty)

    def _get_total_questions(self) -> int:
        """Get total number of questions for GMAT Verbal section."""
        return 23  # Base number for mock generation

    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GMAT Verbal section using nomenclature patterns.

        Returns:
            nomenclature:
            `<questionType> - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []

        # Get section configuration for RC and CR distribution from customizations
        section_config = self.customizations.get("section", {})

        # Determine RC and CR question distribution using random selection
        rc_options = section_config.get("RC", [13, 14])
        num_rc_questions = self.get_random_element(rc_options) if rc_options else 13
        
        cr_options = section_config.get("CR", [10, 9])
        num_cr_questions = self.get_random_element(cr_options) if cr_options else 9

        # Generate prompts using nomenclature patterns
        question_index = 0

        # Generate RC prompts using nomenclature
        for _ in range(num_rc_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for RC
            prompt = self.generate_nomenclature_based_prompt(
                "reading_comprehension",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate CR prompts using nomenclature
        for _ in range(num_cr_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for CR
            prompt = self.generate_nomenclature_based_prompt(
                "critical_reasoning",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        return prompts

    def _get_default_component_allocation(self):
        """
        Get GMAT Verbal specific component allocation.

        Note: This is now primarily loaded from customizations.json file.
        These are fallback defaults if customizations file is not available.
        """
        return {
            "section": {
                "RC": [13, 14],
                "CR": [10, 9]  # Updated to match customizations.json
            }
        }
