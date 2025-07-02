"""
GMAT Quantitative Prompt Generator.

This module provides prompt generation specifically for GMAT Quantitative sections,
handling the specific requirements and question types for GMAT math questions.
"""

import random
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
        Generate question prompts for GMAT Quantitative section.
        
        Returns:
            List of formatted prompt strings for question generation
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)
        
        # Get question styles (DS and Problem Solving)
        question_styles = self.component_allocation.get("question_style", ["DS", "S"])
        
        # Get available topics
        topics = self.component_allocation.get("options", [
            "arithmetic", "algebra", "geometry", "word_problems", 
            "data_analysis", "number_theory"
        ])
        
        for i in range(self.total_questions):
            # Select question style cyclically
            style = self._get_next_element(question_styles, cn + i)
            
            # Select topic cyclically  
            topic = self._get_next_element(topics, cn + i)
            
            # Get focused skill for the selected topic
            topic_config = self.component_allocation.get(topic, {})
            skills = topic_config.get("focused_skill", self._get_default_skills(topic))
            skill = self._get_next_element(skills, cn + i)
            
            # Get difficulty level
            difficulty = difficulty_pool[i] if i < len(difficulty_pool) else 3
            
            # Create the prompt
            prompt = self._create_prompt(style, topic, skill, difficulty)
            prompts.append(prompt)
        
        # Update combination counter for variety
        self._update_combination_counter()
        
        return prompts
    
    def _get_default_skills(self, topic: str) -> List[str]:
        """
        Get default skills for a given topic.
        
        Args:
            topic: The topic name
            
        Returns:
            List of skills for the topic
        """
        default_skills = {
            "arithmetic": [
                "basic_operations", "percentages", "ratios_and_proportions",
                "interest_problems", "profit_and_loss", "mixtures"
            ],
            "algebra": [
                "linear_equations", "quadratic_equations", "inequalities",
                "functions", "sequences", "coordinate_geometry"
            ],
            "geometry": [
                "triangles", "circles", "rectangles_and_squares", 
                "coordinate_geometry", "area_and_perimeter", "volume"
            ],
            "word_problems": [
                "work_and_time", "speed_distance_time", "age_problems",
                "mixture_problems", "investment_problems"
            ],
            "data_analysis": [
                "statistics", "probability", "data_interpretation",
                "mean_median_mode", "standard_deviation", "combinations_permutations"
            ],
            "number_theory": [
                "prime_numbers", "factors_and_multiples", "divisibility",
                "remainder_problems", "number_properties"
            ]
        }
        
        return default_skills.get(topic, ["general"])
    
    def _get_default_component_allocation(self):
        """Get GMAT Quantitative specific component allocation."""
        return {
            "combination_number": 0,
            "question_style": ["DS", "S"],
            "options": [
                "arithmetic", "algebra", "geometry", 
                "word_problems", "data_analysis", "number_theory"
            ],
            "arithmetic": {
                "focused_skill": [
                    "basic_operations", "percentages", "ratios_and_proportions",
                    "interest_problems", "profit_and_loss", "mixtures"
                ]
            },
            "algebra": {
                "focused_skill": [
                    "linear_equations", "quadratic_equations", "inequalities",
                    "functions", "sequences", "coordinate_geometry"
                ]
            },
            "geometry": {
                "focused_skill": [
                    "triangles", "circles", "rectangles_and_squares",
                    "coordinate_geometry", "area_and_perimeter", "volume"
                ]
            },
            "word_problems": {
                "focused_skill": [
                    "work_and_time", "speed_distance_time", "age_problems",
                    "mixture_problems", "investment_problems"
                ]
            },
            "data_analysis": {
                "focused_skill": [
                    "statistics", "probability", "data_interpretation",
                    "mean_median_mode", "standard_deviation", "combinations_permutations"
                ]
            },
            "number_theory": {
                "focused_skill": [
                    "prime_numbers", "factors_and_multiples", "divisibility",
                    "remainder_problems", "number_properties"
                ]
            }
        }