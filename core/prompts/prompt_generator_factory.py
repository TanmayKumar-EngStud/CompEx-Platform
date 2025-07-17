"""
Prompt Generator Factory Module.

This module provides a factory for creating prompt generators based on
exam type and section type. It implements the factory pattern to enable
dynamic prompt generator creation and configuration.
"""

from typing import Dict, Type, Optional
from core.enums.exam_types import ExamType
from core.enums.section_types import SectionType
from core.exceptions.generation_exceptions import PromptGenerationException

from .base.base_prompt_generator import BasePromptGenerator


class PromptGeneratorFactory:
    """
    Factory class for creating prompt generators.

    This factory creates appropriate prompt generators based on exam type
    and section type, handling the selection and configuration of the
    correct generator implementation.

    Example:
        >>> factory = PromptGeneratorFactory()
        >>> generator = factory.create_prompt_generator(
        ...     exam_type=ExamType.GMAT,
        ...     section_type=SectionType.QUANTITATIVE,
        ...     difficulty=3
        ... )
        >>> prompts = generator.generate_question_prompts()
    """

    def __init__(self):
        """Initialize the factory with generator mappings."""
        self._generators: Dict[tuple, Type[BasePromptGenerator]] = {}
        self._register_generators()

    def _register_generators(self):
        """Register all available prompt generators."""
        # Import generators dynamically to avoid circular imports
        try:
            from .gmat.gmat_quants_prompts import GMATQuantsPrompts
            from .gmat.gmat_verbal_prompts import GMATVerbalPrompts
            from .gmat.gmat_ir_prompts import GMATIRPrompts

            self._generators[(
                ExamType.GMAT, SectionType.QUANTITATIVE)] = GMATQuantsPrompts
            self._generators[(ExamType.GMAT, SectionType.VERBAL)
                             ] = GMATVerbalPrompts
            self._generators[(
                ExamType.GMAT, SectionType.INTEGRATED_REASONING)] = GMATIRPrompts

        except ImportError:
            # GMAT generators not available yet, will create below
            pass

        try:
            from .gre.gre_quants_prompts import GREQuantsPrompts
            from .gre.gre_verbal_prompts import GREVerbalPrompts

            self._generators[(
                ExamType.GRE, SectionType.QUANTITATIVE)] = GREQuantsPrompts
            self._generators[(ExamType.GRE, SectionType.VERBAL)
                             ] = GREVerbalPrompts

        except ImportError:
            # GRE generators not available yet, will create below
            pass

    def create_prompt_generator(
        self,
        exam_type: ExamType,
        section_type: SectionType,
        difficulty: int
    ) -> BasePromptGenerator:
        """
        Create a prompt generator for the specified exam and section.

        Args:
            exam_type: The exam type (GMAT or GRE)
            section_type: The section type (QUANTITATIVE, VERBAL, etc.)
            difficulty: Mock exam difficulty level (1-5)

        Returns:
            Configured prompt generator instance

        Raises:
            PromptGenerationException: If no generator is available for the combination
        """
        generator_key = (exam_type, section_type)

        if generator_key not in self._generators:
            # Try to create a default generator for the combination
            generator_class = self._create_default_generator(
                exam_type, section_type)
            if generator_class:
                self._generators[generator_key] = generator_class
            else:
                raise PromptGenerationException(
                    f"No prompt generator available for {exam_type.value} {section_type.value}"
                )

        generator_class = self._generators[generator_key]
        return generator_class(exam_type, section_type, difficulty)

    def _create_default_generator(
        self,
        exam_type: ExamType,
        section_type: SectionType
    ) -> Optional[Type[BasePromptGenerator]]:
        """
        Create a default generator class for exam/section combinations.

        This method creates basic generator classes when specific implementations
        are not available, ensuring the system continues to work.
        """
        class DefaultPromptGenerator(BasePromptGenerator):
            """Default prompt generator for exam/section combinations."""

            def __init__(self, exam_type: ExamType, section_type: SectionType, mock_difficulty: int):
                super().__init__(exam_type, section_type, mock_difficulty)

            def _get_total_questions(self) -> int:
                """Get default number of questions based on exam and section type."""
                if exam_type == ExamType.GMAT:
                    if section_type == SectionType.QUANTITATIVE:
                        return 21  # Base questions for mock
                    elif section_type == SectionType.VERBAL:
                        return 23  # Base questions for mock
                    elif section_type == SectionType.INTEGRATED_REASONING:
                        return 8   # Base questions for mock
                elif exam_type == ExamType.GRE:
                    if section_type == SectionType.QUANTITATIVE:
                        return 15  # Base questions per section
                    elif section_type == SectionType.VERBAL:
                        return 15  # Base questions per section

                return 20  # Default fallback

            def generate_question_prompts(self) -> list[str]:
                """Generate basic question prompts."""
                difficulty_pool = self.get_difficulty_pool()
                prompts = []

                # Get basic configuration
                cn = self.component_allocation.get("combination_number", 0)
                question_styles = self.component_allocation.get(
                    "question_style", ["S"])
                topics = self.component_allocation.get("options")

                for i in range(self.total_questions):
                    # Select elements cyclically
                    style = self._get_next_element(question_styles, cn + i)
                    topic = self._get_next_element(topics, cn + i)

                    # Get skill for this topic
                    topic_config = self.component_allocation.get(topic, {})
                    skills = topic_config.get("focused_skill")
                    skill = self._get_next_element(skills, cn + i)

                    # Create prompt
                    difficulty = difficulty_pool[i] if i < len(
                        difficulty_pool) else 3
                    prompt = self._create_prompt(
                        style, topic, skill, difficulty)
                    prompts.append(prompt)

                self._update_combination_counter()
                return prompts

        return DefaultPromptGenerator

    def register_generator(
        self,
        exam_type: ExamType,
        section_type: SectionType,
        generator_class: Type[BasePromptGenerator]
    ):
        """
        Register a custom prompt generator.

        Args:
            exam_type: The exam type
            section_type: The section type
            generator_class: The generator class to register
        """
        self._generators[(exam_type, section_type)] = generator_class

    def get_available_combinations(self) -> list[tuple[ExamType, SectionType]]:
        """
        Get all available exam/section combinations.

        Returns:
            List of (exam_type, section_type) tuples
        """
        return list(self._generators.keys())
