"""
Base Prompt Generator Module.

This module provides the abstract base class for all prompt generators,
defining the common interface and shared functionality.
"""

import json
import os
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from core.utilities.file_utils import load_json_file
from core.utilities.logging_utils import StructuredLogger


class BasePromptGenerator(ABC):
    """
    Abstract base class for all prompt generators.
    
    This class provides common functionality for generating question prompts
    while allowing exam and section-specific customization through inheritance.
    
    Attributes:
        exam_type: The exam type (GMAT or GRE)
        section_type: The section type (QUANTITATIVE, VERBAL, etc.)
        mock_difficulty: Overall difficulty level of the mock exam
        logger: Structured logger instance
    """
    
    def __init__(
        self, 
        exam_type: ExamType, 
        section_type: SectionType, 
        mock_difficulty: int
    ):
        """
        Initialize the prompt generator.
        
        Args:
            exam_type: The exam type (GMAT or GRE)
            section_type: The section type
            mock_difficulty: Mock exam difficulty level (1-5)
        """
        self.exam_type = exam_type
        self.section_type = section_type
        self.mock_difficulty = mock_difficulty
        self.logger = StructuredLogger(f"PromptGenerator_{exam_type.value}_{section_type.value}")
        
        # Load configuration data
        self.difficulty_distribution = self._load_difficulty_distribution()
        self.component_allocation = self._load_component_allocation()
        
        # Section-specific configurations
        self.total_questions = self._get_total_questions()
        
    @abstractmethod
    def generate_question_prompts(self) -> List[str]:
        """
        Generate question prompts for the section.
        
        Returns:
            List of formatted prompt strings
        """
        pass
    
    @abstractmethod
    def _get_total_questions(self) -> int:
        """
        Get the total number of questions for this section.
        
        Returns:
            Number of questions to generate
        """
        pass
    
    def _load_difficulty_distribution(self) -> Dict[str, Any]:
        """Load difficulty distribution configuration."""
        try:
            # Try to load from unified config first
            config_path = Path("config") / "difficulty_distribution.json"
            if config_path.exists():
                data = load_json_file(str(config_path))
                return data.get(self.section_type.value, {})
            
            # Fallback to exam-specific config
            legacy_path = self._get_legacy_config_path("difficulty_distribution.json")
            if legacy_path and legacy_path.exists():
                data = load_json_file(str(legacy_path))
                section_key = self._get_legacy_section_key()
                return data.get(section_key, {})
            
            # Return default distribution
            return self._get_default_difficulty_distribution()
            
        except Exception as e:
            self.logger.log_generation_error(e, {
                "operation": "load_difficulty_distribution",
                "exam_type": self.exam_type.value,
                "section_type": self.section_type.value
            })
            return self._get_default_difficulty_distribution()
    
    def _load_component_allocation(self) -> Dict[str, Any]:
        """Load component allocation configuration."""
        try:
            # Try to load from unified config first
            config_path = Path("config") / "component_allocation.json"
            if config_path.exists():
                data = load_json_file(str(config_path))
                return data.get(self.section_type.value, {})
            
            # Fallback to exam-specific config
            legacy_path = self._get_legacy_config_path("component_allocation.json")
            if legacy_path and legacy_path.exists():
                data = load_json_file(str(legacy_path))
                section_key = self._get_legacy_section_key()
                return data.get(section_key, {})
            
            # Return default allocation
            return self._get_default_component_allocation()
            
        except Exception as e:
            self.logger.log_generation_error(e, {
                "operation": "load_component_allocation",
                "exam_type": self.exam_type.value,
                "section_type": self.section_type.value
            })
            return self._get_default_component_allocation()
    
    def _get_legacy_config_path(self, filename: str) -> Optional[Path]:
        """Get the path to legacy configuration files."""
        exam_dir = self.exam_type.value.upper()
        section_dir = "Mock_prompts"
        
        base_path = Path(exam_dir) / section_dir / "jsonfiles" / filename
        
        return base_path if base_path.exists() else None
    
    def _get_legacy_section_key(self) -> str:
        """Get the legacy section key for configuration files."""
        if self.section_type == SectionType.QUANTITATIVE:
            return "quants"
        elif self.section_type == SectionType.VERBAL:
            return "verbal"
        elif self.section_type == SectionType.INTEGRATED_REASONING:
            return "integrated_reasoning"
        else:
            return self.section_type.value
    
    def get_difficulty_pool(self) -> List[int]:
        """
        Generate a pool of difficulty levels for questions.
        
        Returns:
            List of difficulty levels (1-5) for each question
        """
        difficulty_ratio = self.difficulty_distribution.get(str(self.mock_difficulty), {})
        
        if not difficulty_ratio:
            # Fallback to balanced distribution
            difficulty_ratio = {"easy": 0.2, "medium": 0.6, "hard": 0.2}
        
        total_questions = self.total_questions + 5  # Add buffer for variety
        
        easy_count = int(total_questions * difficulty_ratio.get("easy", 0.2))
        medium_count = int(total_questions * difficulty_ratio.get("medium", 0.6))
        hard_count = total_questions - (easy_count + medium_count)
        
        # Distribute across difficulty levels 1-5
        one = random.randint(1, max(1, easy_count - 1))
        three = random.randint(1, max(1, medium_count - 1))
        five = random.randint(1, max(1, hard_count - 1))
        
        two_three = random.randint(1, max(1, medium_count - three))
        two = easy_count - one + two_three
        four = hard_count - five + medium_count - three - two_three
        
        # Ensure non-negative counts
        one = max(0, one)
        two = max(0, two)
        three = max(0, three)
        four = max(0, four)
        five = max(0, five)
        
        difficulty_pool = ([1] * one + [2] * two + [3] * three + [4] * four + [5] * five)
        
        # Ensure we have enough difficulties
        while len(difficulty_pool) < self.total_questions:
            difficulty_pool.append(3)  # Add medium difficulty as default
        
        random.shuffle(difficulty_pool)
        return difficulty_pool[:self.total_questions]
    
    def _get_default_difficulty_distribution(self) -> Dict[str, Any]:
        """Get default difficulty distribution."""
        return {
            "1": {"easy": 0.8, "medium": 0.2, "hard": 0.0},
            "2": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
            "3": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
            "4": {"easy": 0.2, "medium": 0.4, "hard": 0.4},
            "5": {"easy": 0.1, "medium": 0.3, "hard": 0.6}
        }
    
    def _get_default_component_allocation(self) -> Dict[str, Any]:
        """Get default component allocation."""
        return {
            "combination_number": 0,
            "question_style": ["DS", "S"],
            "options": ["arithmetic", "algebra", "geometry"],
            "arithmetic": {
                "focused_skill": ["basic_operations", "percentages", "ratios"]
            },
            "algebra": {
                "focused_skill": ["equations", "inequalities", "functions"]
            },
            "geometry": {
                "focused_skill": ["coordinate_geometry", "properties", "area_volume"]
            }
        }
    
    def _create_prompt(
        self, 
        question_style: str, 
        topic: str, 
        skill: str, 
        difficulty: int,
        additional_elements: Optional[List[str]] = None
    ) -> str:
        """
        Create a formatted prompt string.
        
        Args:
            question_style: Style of question (DS, S, RC, etc.)
            topic: Main topic area
            skill: Specific skill being tested
            difficulty: Difficulty level (1-5)
            additional_elements: Optional additional prompt elements
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [question_style]
        
        if topic:
            prompt_parts.append(f"<{topic}>")
        
        if skill:
            prompt_parts.append(f"<{skill}>")
        
        if additional_elements:
            prompt_parts.extend(additional_elements)
        
        prompt_parts.append(f"<difficulty_level: {difficulty}>")
        
        return " - ".join(prompt_parts)
    
    def _update_combination_counter(self):
        """Update the combination counter for variety."""
        if "combination_number" in self.component_allocation:
            self.component_allocation["combination_number"] += 1
    
    def _get_next_element(self, element_list: List[str], combination_number: int) -> str:
        """
        Get the next element from a list using combination number.
        
        Args:
            element_list: List of elements to choose from
            combination_number: Current combination number
            
        Returns:
            Selected element
        """
        if not element_list:
            return ""
        
        index = combination_number % len(element_list)
        
        # Shuffle the list when we complete a cycle
        if index == 0 and combination_number > 0:
            random.shuffle(element_list)
        
        return element_list[index]