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
        Generate question prompts for GMAT Verbal section.
        
        Returns:
            List of formatted prompt strings for question generation
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)
        
        # Get section configuration for RC and CR distribution
        section_config = self.component_allocation.get("section", {})
        
        # Determine RC and CR question distribution
        itr = random.randint(0, 1)
        num_rc_questions = section_config.get("RC", [13, 14])[itr] if section_config.get("RC") else 13
        num_cr_questions = section_config.get("CR", [9, 10])[itr] if section_config.get("CR") else 9
        
        # Create RC prompts
        rc_prompts = self._generate_rc_prompts(num_rc_questions, difficulty_pool, cn)
        prompts.extend(rc_prompts)
        
        # Create CR prompts  
        cr_prompts = self._generate_cr_prompts(
            num_cr_questions, 
            difficulty_pool[len(rc_prompts):], 
            cn + len(rc_prompts)
        )
        prompts.extend(cr_prompts)
        
        # Update combination counter
        self._update_combination_counter()
        
        return prompts
    
    def _generate_rc_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """Generate Reading Comprehension prompts."""
        prompts = []
        
        # RC configurations (3 or 4 questions per passage)
        if num_questions == 13:
            rc_configs = ["RC_3", "RC_3", "RC_3", "RC_4"]
        else:
            rc_configs = ["RC_3", "RC_3", "RC_4", "RC_4"] 
        
        random.shuffle(rc_configs)
        
        # Get themes for RC passages
        themes = self.component_allocation.get("themes", [
            "business", "science", "history", "literature", 
            "sociology", "economics", "technology", "arts"
        ])
        
        question_index = 0
        
        for i, rc_config in enumerate(rc_configs):
            # Number of questions for this passage
            num_passage_questions = int(rc_config.split("_")[1])
            
            # Select theme for this passage
            theme = self._get_next_element(themes, start_cn + i)
            
            # Create prompts for this passage
            for j in range(num_passage_questions):
                difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
                
                # Create RC prompt with passage grouping
                prompt = self._create_prompt(
                    rc_config, 
                    theme, 
                    "reading_comprehension", 
                    difficulty,
                    additional_elements=[f"passage_{i+1}", f"question_{j+1}"]
                )
                
                prompts.append(prompt)
                question_index += 1
        
        return prompts
    
    def _generate_cr_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """Generate Critical Reasoning prompts."""
        prompts = []
        
        # Get CR types
        cr_types = self.component_allocation.get("cr_types", [
            "strengthen", "weaken", "assumption", "inference", 
            "evaluation", "flaw", "parallel_reasoning", "boldface"
        ])
        
        for i in range(num_questions):
            # Select CR type cyclically
            cr_type = self._get_next_element(cr_types, start_cn + i)
            
            difficulty = difficulty_pool[i] if i < len(difficulty_pool) else 3
            
            # Create CR prompt
            prompt = self._create_prompt(
                "CR", 
                "critical_reasoning", 
                cr_type, 
                difficulty
            )
            
            prompts.append(prompt)
        
        return prompts
    
    def _get_default_component_allocation(self):
        """Get GMAT Verbal specific component allocation."""
        return {
            "combination_number": 0,
            "section": {
                "RC": [13, 14],
                "CR": [9, 10]
            },
            "themes": [
                "business", "science", "history", "literature",
                "sociology", "economics", "technology", "arts",
                "environment", "politics", "psychology", "philosophy"
            ],
            "cr_types": [
                "strengthen", "weaken", "assumption", "inference",
                "evaluation", "flaw", "parallel_reasoning", "boldface",
                "method_of_reasoning", "role_of_statement"
            ]
        }