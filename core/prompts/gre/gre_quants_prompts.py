"""
GRE Quantitative Prompt Generator.

This module provides prompt generation specifically for GRE Quantitative sections,
handling the specific requirements and question types for GRE math questions.
"""

from typing import List
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from ..base.base_prompt_generator import BasePromptGenerator


class GREQuantsPrompts(BasePromptGenerator):
    """
    GRE Quantitative prompt generator.
    
    Generates prompts for GRE quantitative questions including Data Sufficiency,
    Numeric Entry, Problem Solving, and Parent-Child (quantitative comparison) questions.
    """
    
    def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
        """Initialize GRE Quantitative prompt generator."""
        super().__init__(exam_type, section_type, mock_difficulty)
    
    def _get_total_questions(self) -> int:
        """Get total number of questions for GRE Quantitative section."""
        # Get total from configuration
        section_config = self.customizations.get("quants", {})
        section1_config = section_config.get("section1", {})
        return section1_config.get("total_questions", 20)
    
    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GRE Quantitative section using nomenclature patterns.
        
        Returns:
            nomenclature:
            Data Sufficiency: `DS - <questionTopic> - <questionTheme> - <questionStyle> - <graphType/tableType> - <difficulty_level: {1-5}>`
            Problem Solving: `S - <questionTopic> - <questionTheme> - <questionStyle> - <graphType/tableType> - <difficulty_level: {1-5}>`
            Numeric Entry: `NE - <questionTopic> - <questionTheme> - <graphType/TableType> - <difficulty_level: {1-5}>`
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get section configuration from customizations
        section_config = self.customizations.get("quants", {})
        
        # Get question distribution based on section (GRE has section1 and section2)
        # For now, using section1 as default pattern
        section1_config = section_config.get("section1", {})
        
        # Question type counts from configuration
        qc_count = section1_config.get("QC", [8, 8])[0]  # Quantitative Comparison (Data Sufficiency style)
        mcq_single_count = section1_config.get("MCQ_Single", [9, 9])[0]  # Problem Solving
        mcq_multiple_count = section1_config.get("MCQ_Multiple", [2, 2])[0]  # Multiple Choice Multiple Answer
        ne_count = section1_config.get("NE", [1, 1])[0]  # Numeric Entry
        
        question_index = 0
        
        # Generate Quantitative Comparison (Data Sufficiency) prompts
        for _ in range(qc_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "data sufficiency",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        # Generate Problem Solving (MCQ Single) prompts
        for _ in range(mcq_single_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "problem solving",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        # Generate MCQ Multiple Answer prompts (also problem solving type)
        for _ in range(mcq_multiple_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "problem solving",  # MCQ_Multiple uses same nomenclature as problem solving
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        # Generate Numeric Entry prompts
        for _ in range(ne_count):
            difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
            prompt = self.generate_nomenclature_based_prompt(
                "numeric entry",
                difficulty
            )
            prompts.append(prompt)
            question_index += 1
        
        return prompts
    
    
    def _get_default_component_allocation(self):
        """
        Get GRE Quantitative specific component allocation.
        
        Note: This is now primarily loaded from customizations.json file.
        These are fallback defaults if customizations file is not available.
        """
        return {
            "section1": {
                "QC": [8, 8],
                "MCQ_Single": [9, 9],
                "NE": [1, 1]
            },
            "section2": {
                "QC": [7, 7],
                "MCQ_Single": [10, 10],
                "NE": [1, 1]
            }
        }