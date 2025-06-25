"""
Generator configuration management for the question generation factory.

This module handles loading and managing generator configurations from
JSON files, providing type-safe access to generator metadata.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..enums.exam_types import ExamType
from ..enums.question_types import QuestionType
from ..enums.section_types import SectionType


@dataclass
class GeneratorMetadata:
    """
    Metadata for a single question generator.
    
    Attributes:
        generator_class: Full import path to the generator class
        question_type: Type of questions this generator creates
        section_type: Section this generator belongs to
        display_name: Human-readable name for the generator
        description: Description of what this generator does
        supports_multi_part: Whether this generator creates multi-part questions
        max_child_questions: Maximum child questions (for multi-part generators)
        system_instruction_file: Path to system instruction file
        example_prompts: List of example prompts for this generator
    """
    generator_class: str
    question_type: QuestionType
    section_type: SectionType
    display_name: str
    description: str
    supports_multi_part: bool = False
    max_child_questions: int = 1
    system_instruction_file: Optional[str] = None
    example_prompts: List[str] = None

    def __post_init__(self):
        """Initialize optional fields."""
        if self.example_prompts is None:
            self.example_prompts = []


@dataclass
class SectionConfig:
    """
    Configuration for a section (Quants, Verbal, IR).
    
    Attributes:
        section_type: Type of this section
        display_name: Human-readable section name
        generators: List of generator metadata for this section
        questions_per_section: Number of questions in this section
        time_limit_minutes: Time limit for this section in minutes
    """
    section_type: SectionType
    display_name: str
    generators: List[GeneratorMetadata]
    questions_per_section: int
    time_limit_minutes: int


@dataclass
class ExamConfig:
    """
    Complete configuration for an exam type.
    
    Attributes:
        exam_type: Type of exam
        display_name: Human-readable exam name
        sections: List of section configurations
        total_time_minutes: Total exam time in minutes
        has_integrated_reasoning: Whether this exam includes IR
    """
    exam_type: ExamType
    display_name: str
    sections: List[SectionConfig]
    total_time_minutes: int
    has_integrated_reasoning: bool


class GeneratorConfig:
    """
    Configuration manager for question generators.
    
    This class loads and manages generator configurations from JSON files,
    providing type-safe access to generator metadata and exam structures.
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self._exam_configs: Dict[ExamType, ExamConfig] = {}
        self._generator_registry: Dict[str, GeneratorMetadata] = {}
        self._loaded = False
    
    def load_configurations(self, config_dir: Optional[str] = None) -> None:
        """
        Load all generator configurations from files.
        
        Args:
            config_dir: Optional custom config directory path
        """
        if self._loaded:
            return
            
        if config_dir is None:
            # Default to config/generators in project root
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config" / "generators"
        else:
            config_dir = Path(config_dir)
        
        # Load GMAT configuration
        gmat_config_path = config_dir / "gmat_generators.json"
        if gmat_config_path.exists():
            self._exam_configs[ExamType.GMAT] = self._load_exam_config(
                gmat_config_path, ExamType.GMAT
            )
        
        # Load GRE configuration  
        gre_config_path = config_dir / "gre_generators.json"
        if gre_config_path.exists():
            self._exam_configs[ExamType.GRE] = self._load_exam_config(
                gre_config_path, ExamType.GRE
            )
        
        self._loaded = True
    
    def _load_exam_config(self, config_path: Path, exam_type: ExamType) -> ExamConfig:
        """
        Load configuration for a specific exam type.
        
        Args:
            config_path: Path to the configuration file
            exam_type: Type of exam being configured
            
        Returns:
            ExamConfig object with loaded configuration
        """
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        sections = []
        for section_data in config_data.get("sections", []):
            generators = []
            
            for gen_data in section_data.get("generators", []):
                # Convert string enum values to actual enums
                question_type = QuestionType(gen_data["question_type"])
                section_type = SectionType(section_data["section_type"])
                
                metadata = GeneratorMetadata(
                    generator_class=gen_data["generator_class"],
                    question_type=question_type,
                    section_type=section_type,
                    display_name=gen_data["display_name"],
                    description=gen_data["description"],
                    supports_multi_part=gen_data.get("supports_multi_part", False),
                    max_child_questions=gen_data.get("max_child_questions", 1),
                    system_instruction_file=gen_data.get("system_instruction_file"),
                    example_prompts=gen_data.get("example_prompts", [])
                )
                
                generators.append(metadata)
                
                # Register in global registry with unique key
                registry_key = f"{exam_type.value}_{question_type.value}_{section_type.value}"
                self._generator_registry[registry_key] = metadata
            
            section_config = SectionConfig(
                section_type=SectionType(section_data["section_type"]),
                display_name=section_data["display_name"],
                generators=generators,
                questions_per_section=section_data.get("questions_per_section", 10),
                time_limit_minutes=section_data.get("time_limit_minutes", 60)
            )
            sections.append(section_config)
        
        return ExamConfig(
            exam_type=exam_type,
            display_name=config_data.get("display_name", exam_type.value.upper()),
            sections=sections,
            total_time_minutes=config_data.get("total_time_minutes", 180),
            has_integrated_reasoning=config_data.get("has_integrated_reasoning", False)
        )
    
    def get_exam_config(self, exam_type: ExamType) -> Optional[ExamConfig]:
        """
        Get configuration for an exam type.
        
        Args:
            exam_type: Exam type to get configuration for
            
        Returns:
            ExamConfig object or None if not found
        """
        self.load_configurations()
        return self._exam_configs.get(exam_type)
    
    def get_generator_metadata(self, exam_type: ExamType, 
                             question_type: QuestionType,
                             section_type: SectionType) -> Optional[GeneratorMetadata]:
        """
        Get metadata for a specific generator.
        
        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type
            
        Returns:
            GeneratorMetadata object or None if not found
        """
        self.load_configurations()
        registry_key = f"{exam_type.value}_{question_type.value}_{section_type.value}"
        return self._generator_registry.get(registry_key)
    
    def get_available_generators(self, exam_type: ExamType) -> List[GeneratorMetadata]:
        """
        Get all available generators for an exam type.
        
        Args:
            exam_type: Exam type to get generators for
            
        Returns:
            List of GeneratorMetadata objects
        """
        self.load_configurations()
        exam_config = self._exam_configs.get(exam_type)
        if not exam_config:
            return []
        
        generators = []
        for section in exam_config.sections:
            generators.extend(section.generators)
        
        return generators
    
    def get_generators_by_section(self, exam_type: ExamType, 
                                section_type: SectionType) -> List[GeneratorMetadata]:
        """
        Get generators for a specific section of an exam.
        
        Args:
            exam_type: Exam type
            section_type: Section type
            
        Returns:
            List of GeneratorMetadata objects for the section
        """
        self.load_configurations()
        exam_config = self._exam_configs.get(exam_type)
        if not exam_config:
            return []
        
        for section in exam_config.sections:
            if section.section_type == section_type:
                return section.generators
        
        return []
    
    def reload_configurations(self) -> None:
        """Force reload of all configurations."""
        self._loaded = False
        self._exam_configs.clear()
        self._generator_registry.clear()
        self.load_configurations()


# Global configuration instance
_config_instance: Optional[GeneratorConfig] = None


def get_generator_config() -> GeneratorConfig:
    """
    Get the global generator configuration instance.
    
    Returns:
        Singleton GeneratorConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = GeneratorConfig()
    return _config_instance