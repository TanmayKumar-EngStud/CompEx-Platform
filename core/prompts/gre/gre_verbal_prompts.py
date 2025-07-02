"""
GRE Verbal Prompt Generator.

This module provides prompt generation specifically for GRE Verbal sections,
handling Reading Comprehension, Text Completion, and Sentence Equivalence question types.
"""

import random
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
        Generate question prompts for GRE Verbal section.
        
        Returns:
            List of formatted prompt strings for question generation
        """
        difficulty_pool = self.get_difficulty_pool()
        prompts = []
        
        # Get combination number for variety
        cn = self.component_allocation.get("combination_number", 0)
        
        # GRE Verbal question type distribution (typical for one section)
        # Reading Comprehension: 4-5 questions (from 1-2 passages)
        # Text Completion: 5-6 questions
        # Sentence Equivalence: 4-5 questions
        
        rc_questions = 4
        tc_questions = 6
        se_questions = 5
        
        # Generate RC prompts
        rc_prompts = self._generate_rc_prompts(rc_questions, difficulty_pool[:rc_questions], cn)
        prompts.extend(rc_prompts)
        
        # Generate TC prompts
        tc_start = len(rc_prompts)
        tc_prompts = self._generate_tc_prompts(
            tc_questions, 
            difficulty_pool[tc_start:tc_start + tc_questions], 
            cn + tc_start
        )
        prompts.extend(tc_prompts)
        
        # Generate SE prompts
        se_start = tc_start + tc_questions
        se_prompts = self._generate_se_prompts(
            se_questions,
            difficulty_pool[se_start:se_start + se_questions],
            cn + se_start
        )
        prompts.extend(se_prompts)
        
        # Update combination counter
        self._update_combination_counter()
        
        return prompts
    
    def _generate_rc_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """Generate Reading Comprehension prompts."""
        prompts = []
        
        # Determine passage configuration
        if num_questions <= 3:
            # Single passage with multiple questions
            rc_configs = [f"rc-s"] * num_questions  # Short passage
        elif num_questions <= 5:
            # Mix of short and medium passages
            rc_configs = [f"rc-m"] * (num_questions // 2) + [f"rc-s"] * (num_questions - num_questions // 2)
        else:
            # Mix of all passage types
            rc_configs = [f"rc-l"] * 2 + [f"rc-m"] * 2 + [f"rc-s"] * (num_questions - 4)
        
        # Get themes for RC passages
        themes = self.component_allocation.get("themes", [
            "science", "humanities", "social_sciences", "literature",
            "history", "philosophy", "arts", "current_events"
        ])
        
        # Group questions by passage
        passage_id = 1
        for i, rc_config in enumerate(rc_configs):
            theme = self._get_next_element(themes, start_cn + i)
            difficulty = difficulty_pool[i] if i < len(difficulty_pool) else 3
            
            # Determine if this starts a new passage
            if i == 0 or rc_config != rc_configs[i-1]:
                passage_id += 1
            
            prompt = self._create_prompt(
                rc_config.upper().replace("-", "_"),
                theme,
                "reading_comprehension",
                difficulty,
                additional_elements=[f"passage_{passage_id}"]
            )
            
            prompts.append(prompt)
        
        return prompts
    
    def _generate_tc_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """Generate Text Completion prompts."""
        prompts = []
        
        # Text Completion types (by number of blanks)
        tc_types = ["TC_1", "TC_2", "TC_3"]  # 1, 2, or 3 blanks
        tc_distribution = [3, 2, 1]  # Most questions have 1 blank, fewer have 2-3
        
        # Get topics for TC
        topics = self.component_allocation.get("tc_topics", [
            "academic", "literary", "scientific", "historical",
            "philosophical", "cultural", "social", "economic"
        ])
        
        question_index = 0
        for tc_type, count in zip(tc_types, tc_distribution):
            for i in range(min(count, num_questions - question_index)):
                topic = self._get_next_element(topics, start_cn + question_index)
                difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
                
                prompt = self._create_prompt(
                    tc_type,
                    topic,
                    "text_completion",
                    difficulty
                )
                
                prompts.append(prompt)
                question_index += 1
                
                if question_index >= num_questions:
                    break
        
        return prompts
    
    def _generate_se_prompts(self, num_questions: int, difficulty_pool: List[int], start_cn: int) -> List[str]:
        """Generate Sentence Equivalence prompts."""
        prompts = []
        
        # Get topics for SE
        topics = self.component_allocation.get("se_topics", [
            "vocabulary", "context_clues", "word_relationships",
            "academic_vocabulary", "formal_writing", "technical_terms"
        ])
        
        for i in range(num_questions):
            topic = self._get_next_element(topics, start_cn + i)
            difficulty = difficulty_pool[i] if i < len(difficulty_pool) else 3
            
            prompt = self._create_prompt(
                "SE",
                topic,
                "sentence_equivalence",
                difficulty
            )
            
            prompts.append(prompt)
        
        return prompts
    
    def _get_default_component_allocation(self):
        """Get GRE Verbal specific component allocation."""
        return {
            "combination_number": 0,
            "themes": [
                "science", "humanities", "social_sciences", "literature",
                "history", "philosophy", "arts", "current_events",
                "technology", "environment", "psychology", "education"
            ],
            "tc_topics": [
                "academic", "literary", "scientific", "historical",
                "philosophical", "cultural", "social", "economic",
                "artistic", "political", "technological", "environmental"
            ],
            "se_topics": [
                "vocabulary", "context_clues", "word_relationships",
                "academic_vocabulary", "formal_writing", "technical_terms",
                "synonyms", "nuanced_meanings", "register", "connotation"
            ],
            "question_types": {
                "RC": ["rc-s", "rc-m", "rc-l"],  # Short, medium, long passages
                "TC": ["TC_1", "TC_2", "TC_3"],  # 1, 2, 3 blanks
                "SE": ["SE"]  # Sentence equivalence
            }
        }