"""
GRE Verbal Prompt Generator.

This module provides prompt generation specifically for GRE Verbal sections,
handling Reading Comprehension, Text Completion, and Sentence Equivalence question types.
"""

from typing import List, Dict, Any
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from ..base.base_prompt_generator import BasePromptGenerator


class GREVerbalPrompts(BasePromptGenerator):
    """
    GRE Verbal prompt generator.
    
    Generates prompts for GRE verbal questions including Reading Comprehension,
    Text Completion, and Sentence Equivalence with appropriate distributions.
    """
    
    def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
        """Initialize GRE Verbal prompt generator."""
        super().__init__(exam_type, section_type, mock_difficulty)
    
    def _get_total_questions(self) -> int:
        """Get total number of questions for GRE Verbal section."""
        return 15  # Base number per section (GRE has 2 verbal sections)
    
    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GRE Verbal section using nomenclature patterns.
        
        Returns:
            nomenclature:
            RC: `<questionType> - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}> - <paragraphs_{1-3}> - <child_questions_{2-4}>`
            TC: `<questionType> - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
            SE: `<SE> - <questionTheme> - <focused_skill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get section configuration from customizations
        section_config = self.customizations.get("verbal", {})
        
        # Get question distribution based on section (GRE has section1 and section2)
        # For now, using section1 as default pattern
        section1_config = section_config.get("section1", {})
        
        # Question type counts
        rc_count = section1_config.get("RC", [10, 10])[0]  # Reading Comprehension
        tc_count = section1_config.get("TC", [6, 6])[0]   # Text Completion
        se_count = section1_config.get("SE", [4, 4])[0]   # Sentence Equivalence
        
        # Calculate total child questions for RC to maintain constant total
        total_child_questions = self._calculate_rc_child_questions(rc_count)
        
        # Adjust total questions to maintain constant count
        # Total questions = RC parent + RC child + TC + SE
        total_questions_needed = self._get_total_questions()
        remaining_questions = total_questions_needed - tc_count - se_count - total_child_questions
        
        # Ensure we have enough RC parent questions
        if remaining_questions < rc_count:
            rc_count = remaining_questions
        
        question_index = 0
        
        # Generate RC prompts using nomenclature and store configurations
        rc_configurations = []
        for _ in range(rc_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            
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
        
        # TEMPORARILY COMMENTED OUT: Generate TC prompts using nomenclature
        # for _ in range(tc_count):
        #     difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
        #     
        #     # Use nomenclature-based generation for TC
        #     prompt = self.generate_nomenclature_based_prompt(
        #         "text completion",
        #         difficulty
        #     )
        #     prompts.append(prompt)
        #     question_index += 1
        
        # TEMPORARILY COMMENTED OUT: Generate SE prompts using nomenclature
        # for _ in range(se_count):
        #     difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
        #     
        #     # Use nomenclature-based generation for SE
        #     prompt = self.generate_nomenclature_based_prompt(
        #         "sentence equivalence",
        #         difficulty
        #     )
        #     prompts.append(prompt)
        #     question_index += 1
        
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
                child_count = rc_config.get('config', {}).get('child_questions', 2)
                total_child_questions += child_count
            return total_child_questions
        else:
            # Fallback: calculate based on random distribution
            rc_config = self.customizations.get("reading comprehension", {})
            question_type_config = rc_config.get("questionType", {})

            if not question_type_config:
                return num_rc_questions * 2  # Fallback: 2 children per parent (GRE average)

            # Get available RC types and their child question counts
            rc_types = list(question_type_config.keys())
            total_child_questions = 0

            # Distribute RC questions across types and calculate total child questions
            for _ in range(num_rc_questions):
                selected_type = self.get_random_element(rc_types)
                type_config = question_type_config.get(selected_type, {})
                child_count = type_config.get("child_questions", 2)
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
        Get GRE Verbal specific component allocation.
        
        Note: This is now primarily loaded from customizations.json file.
        These are fallback defaults if customizations file is not available.
        """
        return {
            "section1": {
                "RC": [10, 10],
                "TC": [6, 6],
                "SE": [4, 4]
            },
            "section2": {
                "RC": [10, 10],
                "TC": [6, 6],
                "SE": [4, 4]
            }
        }