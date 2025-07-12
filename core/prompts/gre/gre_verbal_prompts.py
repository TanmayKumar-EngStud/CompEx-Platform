"""
GRE Verbal Prompt Generator.

This module provides prompt generation specifically for GRE Verbal sections,
handling Reading Comprehension, Text Completion, and Sentence Equivalence question types.
"""

from typing import List
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
            `<questionType> - <questionTheme> - <focusedSkill> - <vocabulary_level: {1-3}> - <difficulty_level: {1-5}>`
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
        
        question_index = 0
        
        # Generate RC prompts using nomenclature
        for _ in range(rc_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            
            # Randomly select RC type from available types
            rc_types = ["rc-s", "rc-m", "rc-l"]
            rc_type = self.get_random_element(rc_types)
            
            prompt = self.generate_nomenclature_based_prompt(
                rc_type,
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        # Generate TC prompts using nomenclature
        for _ in range(tc_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            
            # Randomly select TC type from available types
            tc_types = ["tc-1", "tc-2", "tc-3"]
            tc_type = self.get_random_element(tc_types)
            
            prompt = self.generate_nomenclature_based_prompt(
                tc_type,
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        # Generate SE prompts using nomenclature
        for _ in range(se_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            
            prompt = self.generate_nomenclature_based_prompt(
                "sentence equivalence",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        return prompts
    
    
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