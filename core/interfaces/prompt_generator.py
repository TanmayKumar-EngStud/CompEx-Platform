"""
Abstract interface for prompt generators.

This module defines the protocol that all prompt generators must implement,
ensuring consistent prompt generation across different exam types and sections.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from ..enums.exam_types import ExamType
from ..enums.section_types import SectionType
from ..enums.question_types import QuestionType
from ..enums.difficulty_levels import DifficultyLevel


@runtime_checkable
class IPromptGenerator(Protocol):
    """
    Protocol defining the interface for prompt generators.

    This protocol ensures that all prompt generators implement
    the required methods for generating consistent, high-quality prompts.
    """

    def generate_prompts(self, section_type: SectionType,
                         difficulty: DifficultyLevel,
                         question_count: int) -> List[str]:
        """
        Generate prompts for a specific section.

        Args:
            section_type: Type of section to generate prompts for
            difficulty: Target difficulty level
            question_count: Number of prompts to generate

        Returns:
            List of prompt strings
        """
        ...

    def generate_single_prompt(self, question_type: QuestionType,
                               difficulty: DifficultyLevel,
                               topic: Optional[str] = None,
                               skill: Optional[str] = None) -> str:
        """
        Generate a single prompt for a specific question type.

        Args:
            question_type: Type of question to generate prompt for
            difficulty: Target difficulty level
            topic: Optional specific topic
            skill: Optional specific skill to focus on

        Returns:
            Generated prompt string
        """
        ...

    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections this prompt generator supports.

        Returns:
            List of supported section types
        """
        ...

    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator supports.

        Returns:
            Exam type enum value
        """
        ...


class BasePromptGenerator(ABC):
    """
    Abstract base class for prompt generators.

    This class provides common functionality and enforces the implementation
    of required methods for all prompt generators.
    """

    def __init__(self, exam_type: ExamType):
        """
        Initialize the base prompt generator.

        Args:
            exam_type: The exam type this generator supports
        """
        self.exam_type = exam_type
        self._combination_trackers = {}  # Track combinations to ensure variety
        self._customization_data = self._load_customization_data()

    def _load_customization_data(self) -> Dict[str, Any]:
        """
        Load customization data from the appropriate JSON file.

        Returns:
            Dictionary containing customization data
        """
        from ..utilities.file_utils import load_json_file, get_project_root

        exam_name = self.exam_type.value.lower()
        customizations_file = get_project_root() / "system_instructions" / \
            exam_name / "customizations.json"

        data = load_json_file(customizations_file)
        if data is None:
            return {}
        return data

    @abstractmethod
    def generate_prompts(self, section_type: SectionType,
                         difficulty: DifficultyLevel,
                         question_count: int) -> List[str]:
        """
        Generate prompts for a specific section.

        This method must be implemented by concrete generator classes.

        Args:
            section_type: Type of section to generate prompts for
            difficulty: Target difficulty level
            question_count: Number of prompts to generate

        Returns:
            List of prompt strings
        """
        pass

    @abstractmethod
    def generate_single_prompt(self, question_type: QuestionType,
                               difficulty: DifficultyLevel,
                               topic: Optional[str] = None,
                               skill: Optional[str] = None) -> str:
        """
        Generate a single prompt for a specific question type.

        This method must be implemented by concrete generator classes.

        Args:
            question_type: Type of question to generate prompt for
            difficulty: Target difficulty level
            topic: Optional specific topic
            skill: Optional specific skill to focus on

        Returns:
            Generated prompt string
        """
        pass

    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections this prompt generator supports.

        Returns:
            List of supported section types
        """
        return SectionType.get_supported_sections(self.exam_type)

    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator supports.

        Returns:
            Exam type enum value
        """
        return self.exam_type

    def load_combination_data(self, section_type: SectionType) -> Dict[str, Any]:
        """
        Load combination data for ensuring variety in prompt generation.

        Args:
            section_type: Section type to load combinations for

        Returns:
            Dictionary containing combination data
        """
        from ..utilities.file_utils import load_json_file, get_data_directory

        combinations_file = (get_data_directory() / "combinations" /
                             f"{self.exam_type.value}_{section_type.value}_combinations.json")

        combinations = load_json_file(combinations_file)
        if combinations is None:
            # Return default structure if file doesn't exist
            combinations = self._create_default_combinations(section_type)

        return combinations

    def save_combination_data(self, section_type: SectionType, combinations: Dict[str, Any]) -> bool:
        """
        Save updated combination data.

        Args:
            section_type: Section type to save combinations for
            combinations: Combination data to save

        Returns:
            True if saved successfully, False otherwise
        """
        from ..utilities.file_utils import save_json_file, get_data_directory

        combinations_file = (get_data_directory() / "combinations" /
                             f"{self.exam_type.value}_{section_type.value}_combinations.json")

        return save_json_file(combinations, combinations_file)

    def _create_default_combinations(self, section_type: SectionType) -> Dict[str, Any]:
        """
        Create default combination structure for a section.

        Args:
            section_type: Section type to create defaults for

        Returns:
            Default combination dictionary
        """
        return {
            "topics": [],
            "skills": [],
            "question_types": [],
            "used_combinations": []
        }

    def select_topic_and_skill(self, section_type: SectionType,
                               question_type: QuestionType) -> tuple[str, str]:
        """
        Select topic and skill randomly

        Args:
            section_type: Section type
            question_type: Question type

        Returns:
            Tuple of (topic, skill)
        """
        import random

        # Get available topics and skills
        topics = self._get_topics_for_section(section_type)
        skills = self._get_skills_for_section(section_type, question_type)

        # Pure random selection without combination validation
        selected_topic = random.choice(topics)
        selected_skill = random.choice(skills)

        return selected_topic, selected_skill

    def _get_topics_for_section(self, section_type: SectionType) -> List[str]:
        """
        Get available topics for a section type from customization data.

        Args:
            section_type: Section type

        Returns:
            List of topic strings
        """
        section_name = section_type.value.lower()
        if self.exam_type == ExamType.GMAT:
            section_key = "quants" if section_name == "quantitative" else section_name
        else:
            section_key = section_name

        section_data = self._customization_data.get(section_key, {})

        topics = []
        if section_data:
            for key, value in section_data.items():
                if isinstance(value, dict) and "questionTopic" in value:
                    topics.extend(value["questionTopic"].keys())

        return list(set(topics))

    def _get_skills_for_section(self, section_type: SectionType, question_type: QuestionType) -> List[str]:
        """
        Get available skills for a section type and question type from customization data.

        Args:
            section_type: Section type
            question_type: Question type

        Returns:
            List of skill strings
        """
        section_name = section_type.value.lower()
        if self.exam_type == ExamType.GMAT:
            section_key = "quants" if section_name == "quantitative" else section_name
        else:
            section_key = section_name

        section_data = self._customization_data.get(section_key, {})

        skills = []
        if section_data:
            # Normalize question_type name for matching keys in JSON
            qt_name = question_type.value.lower().replace("_", " ")

            for key, value in section_data.items():
                # Direct match (e.g., "critical reasoning")
                if qt_name in key.lower() and isinstance(value, dict) and "focused_skill" in value:
                    skills.extend(value["focused_skill"])
                # Handle nested structures (e.g., GMAT Quants has "problem solving")
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if qt_name in sub_key.lower() and isinstance(sub_value, dict) and "focused_skill" in sub_value:
                            skills.extend(sub_value["focused_skill"])

        return list(set(skills))

    def format_prompt(self, question_type: QuestionType,
                      topic: str, skill: str,
                      difficulty: DifficultyLevel,
                      additional_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a standard prompt string.

        Args:
            question_type: Type of question
            topic: Question topic
            skill: Skill being tested
            difficulty: Difficulty level
            additional_params: Optional additional parameters

        Returns:
            Formatted prompt string
        """
        base_prompt = f"{question_type.short_name} - <{topic}> - <{skill}> - <difficulty_level: {difficulty.value}>"

        if additional_params:
            for key, value in additional_params.items():
                base_prompt += f" - <{key}: {value}>"

        return base_prompt

    def get_question_type_distribution(self, section_type: SectionType) -> Dict[QuestionType, float]:
        """
        Get the distribution of question types for a section.

        Args:
            section_type: Section type

        Returns:
            Dictionary mapping question types to their proportions (0.0-1.0)
        """
        question_types = QuestionType.get_section_questions(
            section_type, self.exam_type)

        if not question_types:
            return {}

        # Default to equal distribution
        equal_weight = 1.0 / len(question_types)
        return {qt: equal_weight for qt in question_types}

    def distribute_questions_by_type(self, section_type: SectionType,
                                     total_questions: int) -> Dict[QuestionType, int]:
        """
        Distribute questions across different types for a section.

        Args:
            section_type: Section type
            total_questions: Total number of questions to distribute

        Returns:
            Dictionary mapping question types to question counts
        """
        distribution = self.get_question_type_distribution(section_type)

        if not distribution:
            return {}

        result = {}
        remaining_questions = total_questions

        # Assign questions based on distribution
        for question_type, proportion in distribution.items():
            count = int(total_questions * proportion)
            result[question_type] = count
            remaining_questions -= count

        # Distribute remaining questions to maintain total
        question_types = list(distribution.keys())
        for i in range(remaining_questions):
            question_type = question_types[i % len(question_types)]
            result[question_type] += 1

        return result


# Type alias for convenience
PromptGeneratorType = IPromptGenerator
