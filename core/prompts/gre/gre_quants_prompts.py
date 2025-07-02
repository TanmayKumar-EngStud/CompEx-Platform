"""
GRE Quantitative Prompt Generator.

This module provides prompt generation specifically for GRE Quantitative sections,
handling the specific requirements and question types for GRE math questions.
"""

import random
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
        return 15  # Base number per section (GRE has 2 quant sections)
    
    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for GRE Quantitative section.
        
        Returns:
            List of formatted prompt strings for question generation
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)
        
        # GRE Quantitative question type distribution
        question_types = ["S", "DS", "NE", "PC"]  # Problem Solving, Data Sufficiency, Numeric Entry, Parent-Child
        type_distribution = {
            "S": 8,   # Problem Solving (most common)
            "DS": 3,  # Quantitative Comparison (Data Sufficiency style)
            "NE": 2,  # Numeric Entry
            "PC": 2   # Parent-Child (shared data)
        }
        
        # Get available topics
        topics = self.component_allocation.get("options", [
            "arithmetic", "algebra", "geometry", "data_analysis"
        ])
        
        question_index = 0
        
        for question_type, count in type_distribution.items():
            for i in range(count):
                if question_index >= self.total_questions:
                    break
                
                # Select topic cyclically
                topic = self._get_next_element(topics, cn + question_index)
                
                # Get focused skill for the selected topic
                topic_config = self.component_allocation.get(topic, {})
                skills = topic_config.get("focused_skill", self._get_default_skills(topic))
                skill = self._get_next_element(skills, cn + question_index)
                
                # Get difficulty level
                difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
                
                # Create the prompt based on question type
                if question_type == "PC":
                    # Parent-Child questions need special formatting
                    prompt = self._create_pc_prompt(topic, skill, difficulty)
                elif question_type == "NE":
                    # Numeric Entry questions
                    prompt = self._create_prompt(question_type, topic, skill, difficulty, ["numeric_answer"])
                else:
                    # Standard questions
                    prompt = self._create_prompt(question_type, topic, skill, difficulty)
                
                prompts.append(prompt)
                question_index += 1
        
        # Update combination counter for variety
        self._update_combination_counter()
        
        return prompts
    
    def _create_pc_prompt(self, topic: str, skill: str, difficulty: int) -> str:
        """Create Parent-Child (shared data) prompt."""
        # PC questions share data across multiple questions
        data_types = ["graph", "table", "chart", "diagram"]
        data_type = random.choice(data_types)
        
        return self._create_prompt(
            "PC", 
            topic, 
            skill, 
            difficulty,
            additional_elements=[f"shared_{data_type}"]
        )
    
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
                "integers", "fractions", "decimals", "percentages",
                "ratios_and_proportions", "exponents_and_roots"
            ],
            "algebra": [
                "linear_equations", "quadratic_equations", "inequalities",
                "functions", "coordinate_geometry", "sequences"
            ],
            "geometry": [
                "lines_and_angles", "triangles", "quadrilaterals", "circles",
                "three_dimensional_figures", "coordinate_geometry"
            ],
            "data_analysis": [
                "descriptive_statistics", "probability", "data_interpretation",
                "counting_methods", "distributions", "graphical_methods"
            ]
        }
        
        return default_skills.get(topic, ["general"])
    
    def _get_default_component_allocation(self):
        """Get GRE Quantitative specific component allocation."""
        return {
            "combination_number": 0,
            "question_style": ["S", "DS", "NE", "PC"],
            "options": ["arithmetic", "algebra", "geometry", "data_analysis"],
            "arithmetic": {
                "focused_skill": [
                    "integers", "fractions", "decimals", "percentages",
                    "ratios_and_proportions", "exponents_and_roots"
                ]
            },
            "algebra": {
                "focused_skill": [
                    "linear_equations", "quadratic_equations", "inequalities",
                    "functions", "coordinate_geometry", "sequences"
                ]
            },
            "geometry": {
                "focused_skill": [
                    "lines_and_angles", "triangles", "quadrilaterals", "circles",
                    "three_dimensional_figures", "coordinate_geometry"
                ]
            },
            "data_analysis": {
                "focused_skill": [
                    "descriptive_statistics", "probability", "data_interpretation",
                    "counting_methods", "distributions", "graphical_methods"
                ]
            }
        }