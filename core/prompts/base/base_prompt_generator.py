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
        self.customizations = self._load_customizations()
        
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
    
    def _load_customizations(self) -> Dict[str, Any]:
        """Load customizations configuration with nomenclature patterns."""
        try:
            # Load from system_instructions directory
            exam_name = self.exam_type.value.lower()
            customizations_path = Path("system_instructions") / exam_name / "customizations.json"
            
            if customizations_path.exists():
                return load_json_file(str(customizations_path))
            
            # Return empty config if file doesn't exist
            return {}
            
        except Exception as e:
            self.logger.log_generation_error(e, {
                "operation": "load_customizations",
                "exam_type": self.exam_type.value,
                "section_type": self.section_type.value
            })
            return {}
    
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
    
    def generate_nomenclature_based_prompt(
        self, 
        question_type: str, 
        difficulty: int
    ) -> str:
        """
        Generate prompt based on nomenclature pattern from customizations.json using random selection.
        
        Args:
            question_type: Type of question (e.g., 'data sufficiency', 'problem solving')
            difficulty: Difficulty level (1-5)
            
        Returns:
            Formatted prompt string based on nomenclature pattern
        """
        section_key = self._get_legacy_section_key()
        section_config = self.customizations.get(section_key, {})
        question_config = section_config.get(question_type, {})
        
        # Try to get nomenclature from question-specific config first
        nomenclature = question_config.get("nomenclature", "") if question_config else ""
        
        # If no question-specific nomenclature, use section-level nomenclature
        if not nomenclature:
            nomenclature = section_config.get("nomenclature", "")
        
        # If still no nomenclature found, fallback to basic prompt
        if not nomenclature:
            return self._create_prompt("S", "general", "general", difficulty)
        
        # Use section config as the source for variable values when no question-specific config
        config_to_use = question_config if question_config else section_config
        
        # Parse nomenclature pattern and substitute values using random selection
        return self._substitute_nomenclature_variables(
            nomenclature, config_to_use, difficulty, question_type
        )
    
    def _substitute_nomenclature_variables(
        self, 
        nomenclature: str, 
        question_config: Dict[str, Any], 
        difficulty: int,
        question_type: str = ""
    ) -> str:
        """
        Substitute variables in nomenclature pattern with actual values.
        
        Args:
            nomenclature: Nomenclature pattern string
            question_config: Configuration for this question type
            difficulty: Difficulty level
            
        Returns:
            Prompt with substituted values
        """
        import re
        
        # Find all variables in angle brackets
        variables = re.findall(r'<([^>]+)>', nomenclature)
        
        substituted = nomenclature
        selectors = ["*", "&", "$"]
        selected_type = None
        
        # First pass: determine the type from the first variable with special characters
        for var in variables:
            if any(selector in var for selector in selectors):
                continue
                
            var_values = question_config.get(var, [])
            if var_values and isinstance(var_values, list):
                # Check randomly selected value for type determination
                selected_value = self.get_random_element(var_values)
                
                for selector in selectors:
                    if selector in str(selected_value):
                        selected_type = selector
                        break
                break
        
        # Second pass: substitute all variables
        for var in variables:
            var_clean = var
            
            # Handle difficulty_level specially
            if "difficulty_level:" in var:
                substituted = substituted.replace(f"<{var}>", f"<difficulty_level: {difficulty}>")
                continue
            
            # Handle vocabulary_level specially
            if "vocabulary_level:" in var:
                vocab_level = question_config.get("vocabulary", 3)
                substituted = substituted.replace(f"<{var}>", f"<vocabulary_level: {vocab_level}>")
                continue
            
            # Handle questionType specially - use the passed question_type parameter
            if var == "questionType" and question_type:
                substituted = substituted.replace(f"<{var}>", f"<{question_type}>")
                continue
            
            # Get values for this variable
            var_values = question_config.get(var_clean, [])
            
            if not var_values or not isinstance(var_values, list):
                # Try without special characters
                base_var = var_clean.rstrip("*&$")
                var_values = question_config.get(base_var, [])
                
            if not var_values:
                substituted = substituted.replace(f"<{var}>", "<general>")
                continue
            
            # Apply special character filtering logic
            filtered_values = self._filter_values_by_type(var_values, var_clean, selected_type)
            
            if filtered_values:
                selected_value = self.get_random_element(filtered_values)
                
                # Clean the selected value
                for selector in selectors:
                    selected_value = str(selected_value).replace(selector, '')
                
                substituted = substituted.replace(f"<{var}>", f"<{selected_value}>")
            else:
                substituted = substituted.replace(f"<{var}>", "<general>")
        
        return substituted
    
    def _filter_values_by_type(
        self, 
        values: List[str], 
        variable_name: str, 
        selected_type: Optional[str]
    ) -> List[str]:
        """
        Filter values based on special character logic.
        
        Args:
            values: List of possible values
            variable_name: Variable name (may contain special characters)
            selected_type: The selected type marker (*, &, $)
            
        Returns:
            Filtered list of values
        """
        selectors = ["*", "&", "$"]
        
        # If variable name has special character, check if it matches selected type
        for selector in selectors:
            if selector in variable_name:
                if selected_type == selector:
                    # Return values that have this selector
                    return [v for v in values if v and selector in str(v)]
                else:
                    # Skip this variable as it doesn't match the selected type
                    return []
        
        # Variable has no special character - apply type filtering
        if selected_type:
            # First try to get values that match the selected type
            matching_values = [v for v in values if v and selected_type in str(v)]
            if matching_values:
                return [str(v).replace(selected_type, '') for v in matching_values]
            
            # If no matching values, get values without any special characters
            clean_values = []
            for v in values:
                if not v:
                    continue
                has_selector = any(selector in str(v) for selector in selectors if selector != selected_type)
                if not has_selector:
                    clean_values.append(str(v).replace(selected_type, '') if selected_type in str(v) else str(v))
            return clean_values
        
        # No type selected, return all values without special characters
        return [str(v).replace(s, '') for v in values for s in selectors if v and s in str(v)] or values
    
    def get_random_element(self, element_list: List[str], count: Optional[int] = None):
        """
        Get random element(s) from a list with optional bracket formatting.
        
        Args:
            element_list: List of elements to choose from
            count: Number of elements to select (None for single element)
            
        Returns:
            If count is None: Single string element
            If count is specified: Dict with:
                - "items": List of selected strings
                - "formatted": Formatted string with angle brackets "<item_1/item_2/...>"
        """
        if not element_list:
            if count is None:
                return ""
            else:
                return {"items": [], "formatted": "<general>"}
        
        if count is None:
            # Return single random element
            return random.choice(element_list)
        else:
            # Return multiple elements with formatting
            actual_count = min(count, len(element_list))
            selected_items = random.sample(element_list, actual_count)
            
            if len(selected_items) == 1:
                formatted = f"<{selected_items[0]}>"
            else:
                joined_values = "/".join(selected_items)
                formatted = f"<{joined_values}>"
            
            return {
                "items": selected_items,
                "formatted": formatted
            }