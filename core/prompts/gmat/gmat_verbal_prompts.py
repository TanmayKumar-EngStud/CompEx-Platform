"""
GMAT Verbal Prompt Generator.

This module provides prompt generation specifically for GMAT Verbal sections,
handling Reading Comprehension and Critical Reasoning question types.
"""

import random
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

        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)

        # Get section configuration for RC and CR distribution from customizations
        section_config = self.customizations.get("section", {})

        # Determine RC and CR question distribution
        itr = random.randint(0, 1)
        num_rc_questions = section_config.get(
            "RC", [13, 14])[itr] if section_config.get("RC") else 13
        num_cr_questions = section_config.get(
            "CR", [10, 9])[itr] if section_config.get("CR") else 9

        # Generate prompts using nomenclature patterns
        question_index = 0

        # Generate RC prompts using nomenclature
        for _ in range(num_rc_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for RC
            prompt = self.generate_nomenclature_based_prompt(
                "reading_comprehension",
                cn + question_index,
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Generate CR prompts using nomenclature
        for i in range(num_cr_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for CR
            prompt = self.generate_nomenclature_based_prompt(
                "critical_reasoning",
                cn + question_index,
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        # Update combination counter
        self._update_combination_counter()

        return prompts

    def _generate_rc_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """
        Generate Reading Comprehension prompts.

        Returns:
            nomenclature:
            `rc-s/rc-m/rc-l - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
        """
        prompts = []

        # Get RC configurations from customizations
        question_types = self.customizations.get(
            "questionType", ["rc-s", "rc-m", "rc-l"])
        rc_types = [qt for qt in question_types if qt.startswith("rc-")]

        # Build RC configuration list based on num_questions
        rc_configs = []
        questions_per_type = {
            "rc-s": 2,  # short passages - 2 questions
            "rc-m": 3,  # medium passages - 3 questions
            "rc-l": 4   # long passages - 4 questions
        }

        # Distribute questions across passage types
        remaining_questions = num_questions
        while remaining_questions > 0 and rc_types:
            for rc_type in rc_types:
                if remaining_questions <= 0:
                    break
                questions_for_passage = questions_per_type.get(rc_type, 3)
                if remaining_questions >= questions_for_passage:
                    rc_configs.append(rc_type)
                    remaining_questions -= questions_for_passage

        random.shuffle(rc_configs)

        # Get themes from customizations
        themes = self.customizations.get("questionTheme", [
            "business", "science", "history", "literature",
            "sociology", "economics", "technology", "arts"
        ])

        question_index = 0

        for i, rc_config in enumerate(rc_configs):
            # Number of questions for this passage type
            num_passage_questions = questions_per_type.get(rc_config, 3)

            # Select theme for this passage
            theme = self._get_next_element(themes, start_cn + i)

            # Create prompts for this passage using nomenclature
            for j in range(num_passage_questions):
                difficulty = difficulty_pool[question_index] if question_index < len(
                    difficulty_pool) else 3

                # Use nomenclature-based generation for RC passages
                prompt = self.generate_nomenclature_based_prompt(
                    "reading_comprehension",
                    start_cn + question_index,
                    difficulty
                )

                prompts.append(prompt)
                question_index += 1

        return prompts

    def _generate_cr_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """
        Generate Critical Reasoning prompts.

        Returns:
            nomenclature:
            `critical reasoning - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
        """
        prompts = []

        # Get CR skills from child-question config in customizations
        child_question_config = self.customizations.get("child-question", {})
        cr_skills = child_question_config.get("focused_skill", [
            "strengthen", "weaken", "assumption", "inference",
            "evaluation", "flaw", "parallel_reasoning", "boldface"
        ])

        for i in range(num_questions):
            difficulty = difficulty_pool[i] if i < len(difficulty_pool) else 3

            # Use nomenclature-based generation for CR questions
            prompt = self.generate_nomenclature_based_prompt(
                "critical_reasoning",
                start_cn + i,
                difficulty
            )

            prompts.append(prompt)

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
