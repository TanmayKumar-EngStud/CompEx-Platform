"""
GMAT Verbal Prompt Generator.

This module provides prompt generation specifically for GMAT Verbal sections,
handling Reading Comprehension and Critical Reasoning question types.
"""

from typing import List, Dict, Any
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
        num_rc_questions = self.get_random_element(
            rc_options) if rc_options else 13

        cr_options = section_config.get("CR", [10, 9])
        num_cr_questions = self.get_random_element(
            cr_options) if cr_options else 9

        # Calculate total child questions for RC to maintain constant total
        total_child_questions = self._calculate_rc_child_questions(num_rc_questions)

        # Adjust total questions to maintain constant count
        # Total questions = CR questions + RC parent questions + RC child questions
        total_questions_needed = self._get_total_questions()
        remaining_questions = total_questions_needed - num_cr_questions - total_child_questions

        # Ensure we have enough RC parent questions
        if remaining_questions < num_rc_questions:
            num_rc_questions = remaining_questions

        # Generate prompts using nomenclature patterns
        question_index = 0

        # Generate RC prompts using nomenclature and store configurations
        rc_configurations = []
        for _ in range(num_rc_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for RC
            prompt = self.generate_nomenclature_based_prompt(
                "reading comprehension",
                difficulty
            )
            prompts.append(prompt)
            
            # Store RC configuration for child question calculation
            rc_config = self.get_rc_configuration()
            if rc_config:
                rc_configurations.append(rc_config)
            
            question_index += 1

        # Store RC configurations for later use
        self._rc_configurations = rc_configurations

        # Generate CR prompts using nomenclature
        for _ in range(num_cr_questions):
            difficulty = difficulty_pool[question_index] if question_index < len(
                difficulty_pool) else 3

            # Use nomenclature-based generation for CR
            prompt = self.generate_nomenclature_based_prompt(
                "critical reasoning",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1

        return prompts

    def _calculate_rc_child_questions(self, num_rc_questions: int) -> int:
        """
        Calculate total child questions for RC based on actual generated configurations.

        Args:
            num_rc_questions: Number of RC parent questions

        Returns:
            Total number of child questions for RC
        """
        if hasattr(self, '_rc_configurations') and self._rc_configurations:
            # Use actual RC configurations from generated prompts
            total_child_questions = 0
            for rc_config in self._rc_configurations:
                child_count = rc_config.get('config', {}).get('child_questions', 1)
                total_child_questions += child_count
            return total_child_questions
        else:
            # Fallback: calculate based on random distribution
            rc_config = self.customizations.get("reading comprehension", {})
            question_type_config = rc_config.get("questionType", {})

            if not question_type_config:
                return num_rc_questions  # Fallback: 1 child per parent

            # Get available RC types and their child question counts
            rc_types = list(question_type_config.keys())
            total_child_questions = 0

            # Distribute RC questions across types and calculate total child questions
            for _ in range(num_rc_questions):
                selected_type = self.get_random_element(rc_types)
                type_config = question_type_config.get(selected_type, {})
                child_count = type_config.get("child_questions", 1)
                total_child_questions += child_count

            return total_child_questions

    def get_rc_configurations(self) -> List[Dict[str, Any]]:
        """
        Get the RC configurations for all generated RC prompts.
        
        Returns:
            List of RC configurations with type and config details
        """
        return getattr(self, '_rc_configurations', [])

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
