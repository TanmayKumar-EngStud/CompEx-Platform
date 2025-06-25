"""
Generator registry for managing question generator classes.

This module provides a registry system for dynamically loading and managing
question generator classes, enabling runtime generator discovery and creation.
"""

import importlib
import inspect
from typing import Dict, List, Type, Optional, Any, Callable
from pathlib import Path

from ..enums.exam_types import ExamType
from ..enums.question_types import QuestionType
from ..enums.section_types import SectionType
from ..interfaces.question_generator import IQuestionGenerator, BaseQuestionGenerator
from .generator_config import GeneratorConfig, GeneratorMetadata, get_generator_config


class GeneratorRegistrationError(Exception):
    """Raised when generator registration fails."""
    pass


class GeneratorRegistry:
    """
    Registry for managing question generator classes.

    This class handles dynamic loading, registration, and creation of
    question generator classes based on configuration files.
    """

    def __init__(self):
        """Initialize the generator registry."""
        self._generators: Dict[str, Type[IQuestionGenerator]] = {}
        self._metadata: Dict[str, GeneratorMetadata] = {}
        self._config: GeneratorConfig = get_generator_config()
        self._loaded = False

    def load_generators(self, force_reload: bool = False) -> None:
        """
        Load all generators from configuration.

        Args:
            force_reload: Force reload even if already loaded
        """
        if self._loaded and not force_reload:
            return

        self._config.load_configurations()

        # Load generators for each exam type
        for exam_type in ExamType:
            self._load_exam_generators(exam_type)

        self._loaded = True

    def _load_exam_generators(self, exam_type: ExamType) -> None:
        """
        Load generators for a specific exam type.

        Args:
            exam_type: Exam type to load generators for
        """
        generators = self._config.get_available_generators(exam_type)

        for metadata in generators:
            try:
                generator_class = self._import_generator_class(
                    metadata.generator_class)
                registry_key = self._get_registry_key(
                    exam_type, metadata.question_type, metadata.section_type
                )

                self._generators[registry_key] = generator_class
                self._metadata[registry_key] = metadata

                # print(f"Loaded generator: {metadata.display_name} ({registry_key})")

            except Exception as e:
                print(
                    f"Failed to load generator {metadata.generator_class}: {e}")
                # Don't fail completely - continue loading other generators
                continue

    def _import_generator_class(self, class_path: str) -> Type[IQuestionGenerator]:
        """
        Dynamically import a generator class from its path.

        Args:
            class_path: Full import path to the generator class

        Returns:
            Generator class type

        Raises:
            GeneratorRegistrationError: If import fails
        """
        try:
            # Split module path and class name
            if '.' not in class_path:
                raise GeneratorRegistrationError(
                    f"Invalid class path: {class_path}")

            module_path, class_name = class_path.rsplit('.', 1)

            # Import the module
            module = importlib.import_module(module_path)

            # Get the class from the module
            if not hasattr(module, class_name):
                raise GeneratorRegistrationError(
                    f"Class {class_name} not found in module {module_path}"
                )

            generator_class = getattr(module, class_name)

            # Validate that it's a proper generator class
            if not self._is_valid_generator_class(generator_class):
                raise GeneratorRegistrationError(
                    f"Class {class_path} does not implement IQuestionGenerator"
                )

            return generator_class

        except ImportError as e:
            raise GeneratorRegistrationError(
                f"Failed to import {class_path}: {e}")

    def _is_valid_generator_class(self, cls: Type) -> bool:
        """
        Validate that a class is a proper generator class.

        Args:
            cls: Class to validate

        Returns:
            True if valid generator class
        """
        # Check if it's a class
        if not inspect.isclass(cls):
            return False

        # Check if it implements the required methods
        required_methods = [
            'generate_question', 'validate_output', 'get_supported_types', 'get_exam_type']

        for method_name in required_methods:
            if not hasattr(cls, method_name):
                return False

            method = getattr(cls, method_name)
            if not callable(method):
                return False

        return True

    def _get_registry_key(self, exam_type: ExamType, question_type: QuestionType,
                          section_type: SectionType) -> str:
        """
        Generate a unique registry key for a generator.

        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type

        Returns:
            Unique registry key string
        """
        return f"{exam_type.value}_{question_type.value}_{section_type.value}"

    def register_generator(self, exam_type: ExamType, question_type: QuestionType,
                           section_type: SectionType, generator_class: Type[IQuestionGenerator],
                           metadata: Optional[GeneratorMetadata] = None) -> None:
        """
        Manually register a generator class.

        Args:
            exam_type: Exam type
            question_type: Question type  
            section_type: Section type
            generator_class: Generator class to register
            metadata: Optional metadata for the generator

        Raises:
            GeneratorRegistrationError: If registration fails
        """
        if not self._is_valid_generator_class(generator_class):
            raise GeneratorRegistrationError(
                f"Invalid generator class: {generator_class.__name__}"
            )

        registry_key = self._get_registry_key(
            exam_type, question_type, section_type)

        self._generators[registry_key] = generator_class

        if metadata:
            self._metadata[registry_key] = metadata
        else:
            # Create default metadata
            self._metadata[registry_key] = GeneratorMetadata(
                generator_class=f"{generator_class.__module__}.{generator_class.__name__}",
                question_type=question_type,
                section_type=section_type,
                display_name=generator_class.__name__,
                description=f"Generator for {question_type.value} questions"
            )

    def get_generator_class(self, exam_type: ExamType, question_type: QuestionType,
                            section_type: SectionType) -> Optional[Type[IQuestionGenerator]]:
        """
        Get a generator class by type.

        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type

        Returns:
            Generator class or None if not found
        """
        self.load_generators()
        registry_key = self._get_registry_key(
            exam_type, question_type, section_type)
        return self._generators.get(registry_key)

    def get_generator_metadata(self, exam_type: ExamType, question_type: QuestionType,
                               section_type: SectionType) -> Optional[GeneratorMetadata]:
        """
        Get metadata for a generator.

        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type

        Returns:
            GeneratorMetadata or None if not found
        """
        self.load_generators()
        registry_key = self._get_registry_key(
            exam_type, question_type, section_type)
        return self._metadata.get(registry_key)

    def get_available_generators(self, exam_type: Optional[ExamType] = None) -> List[str]:
        """
        Get list of available generator keys.

        Args:
            exam_type: Optional exam type filter

        Returns:
            List of generator registry keys
        """
        self.load_generators()

        if exam_type is None:
            return list(self._generators.keys())

        # Filter by exam type
        prefix = f"{exam_type.value}_"
        return [key for key in self._generators.keys() if key.startswith(prefix)]

    def get_generators_by_section(self, exam_type: ExamType,
                                  section_type: SectionType) -> List[str]:
        """
        Get generators for a specific section.

        Args:
            exam_type: Exam type
            section_type: Section type

        Returns:
            List of generator registry keys for the section
        """
        self.load_generators()

        prefix = f"{exam_type.value}_"
        suffix = f"_{section_type.value}"

        return [
            key for key in self._generators.keys()
            if key.startswith(prefix) and key.endswith(suffix)
        ]

    def create_generator_instance(self, exam_type: ExamType, question_type: QuestionType,
                                  section_type: SectionType,
                                  init_args: Optional[Dict[str, Any]] = None) -> Optional[IQuestionGenerator]:
        """
        Create an instance of a generator.

        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type
            init_args: Optional initialization arguments

        Returns:
            Generator instance or None if creation fails
        """
        generator_class = self.get_generator_class(
            exam_type, question_type, section_type)

        if generator_class is None:
            return None

        try:
            if init_args:
                return generator_class(**init_args)
            else:
                # Try to create with default arguments
                return generator_class()

        except Exception as e:
            print(f"Failed to create generator instance: {e}")
            return None

    def unregister_generator(self, exam_type: ExamType, question_type: QuestionType,
                             section_type: SectionType) -> bool:
        """
        Unregister a generator.

        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type

        Returns:
            True if unregistered successfully
        """
        registry_key = self._get_registry_key(
            exam_type, question_type, section_type)

        removed = False
        if registry_key in self._generators:
            del self._generators[registry_key]
            removed = True

        if registry_key in self._metadata:
            del self._metadata[registry_key]

        return removed

    def reload_generators(self) -> None:
        """Force reload of all generators."""
        self._loaded = False
        self._generators.clear()
        self._metadata.clear()
        self._config.reload_configurations()
        self.load_generators()


# Global registry instance
_registry_instance: Optional[GeneratorRegistry] = None


def get_generator_registry() -> GeneratorRegistry:
    """
    Get the global generator registry instance.

    Returns:
        Singleton GeneratorRegistry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = GeneratorRegistry()
    return _registry_instance
