"""
GMAT Integrated Reasoning Prompt Generator.

This module provides prompt generation specifically for GMAT Integrated Reasoning sections,
handling GI, TPA, TA, and MSR question types.
"""

import random
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
        Generate question prompts for GMAT Integrated Reasoning section.
        
        Returns:
            List of formatted prompt strings for question generation
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)
        
        # IR question type distribution (typically 2 of each type for 8 questions)
        ir_types = ["GI", "TPA", "TA", "MSR"]
        questions_per_type = 2
        
        question_index = 0
        
        for ir_type in ir_types:
            for i in range(questions_per_type):
                if question_index >= self.total_questions:
                    break
                
                difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
                
                # Generate type-specific prompt
                if ir_type == "GI":
                    prompt = self._generate_gi_prompt(difficulty, cn + question_index)
                elif ir_type == "TPA":
                    prompt = self._generate_tpa_prompt(difficulty, cn + question_index)
                elif ir_type == "TA":
                    prompt = self._generate_ta_prompt(difficulty, cn + question_index)
                elif ir_type == "MSR":
                    prompt = self._generate_msr_prompt(difficulty, cn + question_index)
                else:
                    prompt = self._create_prompt(ir_type, "integrated_reasoning", "analysis", difficulty)
                
                prompts.append(prompt)
                question_index += 1
        
        # Update combination counter
        self._update_combination_counter()
        
        return prompts
    
    def _generate_gi_prompt(self, difficulty: int, cn: int) -> str:
        """Generate Graphic Interpretation prompt."""
        # GI specific elements
        chart_types = ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"]
        topics = ["Economics", "Business", "Science", "Demographics", "Finance"]
        skills = ["Data Interpretation", "Trend Analysis", "Comparison", "Calculation"]
        
        chart_type = self._get_next_element(chart_types, cn)
        topic = self._get_next_element(topics, cn)
        skill = self._get_next_element(skills, cn)
        
        return self._create_prompt(
            "GI", 
            topic, 
            skill, 
            difficulty,
            additional_elements=[chart_type]
        )
    
    def _generate_tpa_prompt(self, difficulty: int, cn: int) -> str:
        """Generate Two-Part Analysis prompt."""
        topics = ["Business Strategy", "Economics", "Logic", "Science", "Operations"]
        skills = ["Analysis", "Evaluation", "Comparison", "Problem Solving"]
        
        topic = self._get_next_element(topics, cn)
        skill = self._get_next_element(skills, cn)
        
        return self._create_prompt("TPA", topic, skill, difficulty)
    
    def _generate_ta_prompt(self, difficulty: int, cn: int) -> str:
        """Generate Table Analysis prompt."""
        topics = ["Business Data", "Scientific Data", "Survey Results", "Financial Data"]
        skills = ["Data Analysis", "Sorting", "Filtering", "Statistical Analysis"]
        
        topic = self._get_next_element(topics, cn)
        skill = self._get_next_element(skills, cn)
        
        return self._create_prompt("TA", topic, skill, difficulty)
    
    def _generate_msr_prompt(self, difficulty: int, cn: int) -> str:
        """Generate Multi-Source Reasoning prompt."""
        topics = ["Business Case", "Research Study", "Policy Analysis", "Market Analysis"]
        skills = ["Integration", "Synthesis", "Evaluation", "Critical Thinking"]
        
        topic = self._get_next_element(topics, cn)
        skill = self._get_next_element(skills, cn)
        
        return self._create_prompt("MSR", topic, skill, difficulty)
    
    def _get_default_component_allocation(self):
        """Get GMAT IR specific component allocation."""
        return {
            "combination_number": 0,
            "question_types": ["GI", "TPA", "TA", "MSR"],
            "gi": {
                "chart_types": ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"],
                "topics": ["Economics", "Business", "Science", "Demographics", "Finance"],
                "skills": ["Data Interpretation", "Trend Analysis", "Comparison", "Calculation"]
            },
            "tpa": {
                "topics": ["Business Strategy", "Economics", "Logic", "Science", "Operations"],
                "skills": ["Analysis", "Evaluation", "Comparison", "Problem Solving"]
            },
            "ta": {
                "topics": ["Business Data", "Scientific Data", "Survey Results", "Financial Data"],
                "skills": ["Data Analysis", "Sorting", "Filtering", "Statistical Analysis"]
            },
            "msr": {
                "topics": ["Business Case", "Research Study", "Policy Analysis", "Market Analysis"],
                "skills": ["Integration", "Synthesis", "Evaluation", "Critical Thinking"]
            }
        }