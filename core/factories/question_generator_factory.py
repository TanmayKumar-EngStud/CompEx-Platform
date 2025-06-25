"""
Question Generator Factory implementation.

This module provides the main factory class for creating question generators
using the Factory Method pattern with dynamic generator registration.
"""

from typing import Dict, Any, Optional, List, Type
import os
from google import genai

from ..enums.exam_types import ExamType
from ..enums.question_types import QuestionType  
from ..enums.section_types import SectionType
from ..interfaces.question_generator import IQuestionGenerator
from .generator_registry import GeneratorRegistry, get_generator_registry
from .generator_config import GeneratorConfig, GeneratorMetadata, get_generator_config


class QuestionGeneratorFactory:
    """
    Factory class for creating question generators.
    
    This factory uses the registry pattern to dynamically create generators
    based on exam type, question type, and section type. It handles
    configuration loading, generator initialization, and provides a
    consistent interface for generator creation.
    """
    
    def __init__(self):
        """Initialize the question generator factory."""
        self._registry: GeneratorRegistry = get_generator_registry()
        self._config: GeneratorConfig = get_generator_config()
        self._system_instructions_cache: Dict[str, str] = {}
    
    def create_generator(self, exam_type: ExamType, question_type: QuestionType,
                        section_type: SectionType, global_state: Any = None,
                        lock: Any = None, api_idx: int = 0, 
                        prompt: str = "") -> Optional[IQuestionGenerator]:
        """
        Create a question generator instance.
        
        Args:
            exam_type: Type of exam (GMAT/GRE)
            question_type: Type of question to generate
            section_type: Section the question belongs to  
            global_state: Shared state object for threading
            lock: Threading lock object
            api_idx: API key index for rotation
            prompt: Generation prompt
            
        Returns:
            Configured generator instance or None if creation fails
        """
        # Get generator class from registry
        generator_class = self._registry.get_generator_class(
            exam_type, question_type, section_type
        )
        
        if generator_class is None:
            print(f"No generator found for {exam_type.value} {question_type.value} {section_type.value}")
            return None
        
        # Get metadata for configuration
        metadata = self._registry.get_generator_metadata(
            exam_type, question_type, section_type
        )
        
        try:
            # Create generator instance with proper initialization
            if self._is_legacy_generator(generator_class):
                # Legacy generator initialization (current pattern)
                return self._create_legacy_generator(
                    generator_class, global_state, lock, api_idx, prompt, metadata
                )
            else:
                # New unified generator initialization
                return self._create_unified_generator(
                    generator_class, exam_type, question_type, global_state, 
                    lock, api_idx, prompt, metadata
                )
                
        except Exception as e:
            print(f"Failed to create generator {generator_class.__name__}: {e}")
            return None
    
    def _is_legacy_generator(self, generator_class: Type) -> bool:
        """
        Check if a generator class uses the legacy initialization pattern.
        
        Args:
            generator_class: Generator class to check
            
        Returns:
            True if legacy pattern, False if unified
        """
        # Check constructor signature to determine pattern
        import inspect
        
        try:
            sig = inspect.signature(generator_class.__init__)
            params = list(sig.parameters.keys())
            
            # Legacy pattern: __init__(self, global_state, lock, api_IDX, prompt)
            legacy_params = ['self', 'global_state', 'lock', 'api_IDX', 'prompt']
            
            # Check if it matches legacy pattern
            if len(params) >= 5 and params[:5] == legacy_params:
                return True
            
            # Alternative legacy check - look for specific parameter names
            if 'global_state' in params and 'api_IDX' in params:
                return True
                
            return False
            
        except Exception:
            # If we can't determine, assume legacy for safety
            return True
    
    def _create_legacy_generator(self, generator_class: Type, global_state: Any,
                               lock: Any, api_idx: int, prompt: str,
                               metadata: Optional[GeneratorMetadata]) -> Optional[IQuestionGenerator]:
        """
        Create a legacy generator instance.
        
        Args:
            generator_class: Legacy generator class
            global_state: Shared state object
            lock: Threading lock
            api_idx: API key index
            prompt: Generation prompt
            metadata: Generator metadata
            
        Returns:
            Legacy generator instance
        """
        try:
            return generator_class(global_state, lock, api_idx, prompt)
        except Exception as e:
            print(f"Failed to create legacy generator: {e}")
            return None
    
    def _create_unified_generator(self, generator_class: Type, exam_type: ExamType,
                                question_type: QuestionType, global_state: Any,
                                lock: Any, api_idx: int, prompt: str,
                                metadata: Optional[GeneratorMetadata]) -> Optional[IQuestionGenerator]:
        """
        Create a unified generator instance.
        
        Args:
            generator_class: Unified generator class
            exam_type: Exam type
            question_type: Question type
            global_state: Shared state object
            lock: Threading lock
            api_idx: API key index
            prompt: Generation prompt
            metadata: Generator metadata
            
        Returns:
            Unified generator instance
        """
        try:
            # Load system instructions if available
            system_instructions = None
            if metadata and metadata.system_instruction_file:
                system_instructions = self._load_system_instructions(
                    metadata.system_instruction_file
                )
            
            # Create API client
            api_key = os.getenv(f"API_{api_idx}")
            if not api_key:
                print(f"API key API_{api_idx} not found")
                return None
            
            llm = genai.Client(api_key=api_key)
            
            # Initialize with unified pattern
            return generator_class(
                exam_type=exam_type,
                question_type=question_type,
                llm=llm,
                system_instructions=system_instructions,
                global_state=global_state,
                lock=lock,
                prompt=prompt
            )
            
        except Exception as e:
            print(f"Failed to create unified generator: {e}")
            return None
    
    def _load_system_instructions(self, instruction_file: str) -> Optional[str]:
        """
        Load system instructions from file with caching.
        
        Args:
            instruction_file: Path to instruction file
            
        Returns:
            System instructions text or None if not found
        """
        if instruction_file in self._system_instructions_cache:
            return self._system_instructions_cache[instruction_file]
        
        try:
            # Try absolute path first
            if os.path.isabs(instruction_file) and os.path.exists(instruction_file):
                instruction_path = instruction_file
            else:
                # Try relative to project root
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent
                instruction_path = project_root / instruction_file
            
            if os.path.exists(instruction_path):
                with open(instruction_path, 'r') as f:
                    instructions = f.read()
                    self._system_instructions_cache[instruction_file] = instructions
                    return instructions
            else:
                print(f"System instruction file not found: {instruction_file}")
                return None
                
        except Exception as e:
            print(f"Failed to load system instructions from {instruction_file}: {e}")
            return None
    
    def get_available_generators(self, exam_type: Optional[ExamType] = None) -> List[str]:
        """
        Get list of available generator types.
        
        Args:
            exam_type: Optional exam type filter
            
        Returns:
            List of available generator identifiers
        """
        return self._registry.get_available_generators(exam_type)
    
    def get_generators_by_section(self, exam_type: ExamType, 
                                 section_type: SectionType) -> List[str]:
        """
        Get generators available for a specific section.
        
        Args:
            exam_type: Exam type
            section_type: Section type
            
        Returns:
            List of generator identifiers for the section
        """
        return self._registry.get_generators_by_section(exam_type, section_type)
    
    def get_generator_metadata(self, exam_type: ExamType, question_type: QuestionType,
                              section_type: SectionType) -> Optional[GeneratorMetadata]:
        """
        Get metadata for a specific generator.
        
        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type
            
        Returns:
            GeneratorMetadata or None if not found
        """
        return self._registry.get_generator_metadata(exam_type, question_type, section_type)
    
    def register_custom_generator(self, exam_type: ExamType, question_type: QuestionType,
                                 section_type: SectionType, generator_class: Type[IQuestionGenerator],
                                 metadata: Optional[GeneratorMetadata] = None) -> bool:
        """
        Register a custom generator at runtime.
        
        Args:
            exam_type: Exam type
            question_type: Question type
            section_type: Section type
            generator_class: Generator class to register
            metadata: Optional metadata
            
        Returns:
            True if registration successful
        """
        try:
            self._registry.register_generator(
                exam_type, question_type, section_type, generator_class, metadata
            )
            return True
        except Exception as e:
            print(f"Failed to register custom generator: {e}")
            return False
    
    def reload_configurations(self) -> None:
        """Force reload of all configurations and generators."""
        self._registry.reload_generators()
        self._system_instructions_cache.clear()
    
    def create_generator_from_legacy_enum(self, exam_type: ExamType, 
                                        generator_enum_value: str,
                                        global_state: Any = None, lock: Any = None,
                                        api_idx: int = 0, prompt: str = "") -> Optional[IQuestionGenerator]:
        """
        Create generator from legacy enum values for backward compatibility.
        
        Args:
            exam_type: Exam type
            generator_enum_value: Legacy generator enum value (e.g., "Q_DS_gen")
            global_state: Shared state object
            lock: Threading lock
            api_idx: API key index
            prompt: Generation prompt
            
        Returns:
            Generator instance or None if not found
        """
        # Map legacy enum values to question/section types
        legacy_mapping = self._get_legacy_mapping()
        
        if generator_enum_value not in legacy_mapping:
            print(f"Unknown legacy generator: {generator_enum_value}")
            return None
        
        question_type, section_type = legacy_mapping[generator_enum_value]
        
        return self.create_generator(
            exam_type, question_type, section_type, 
            global_state, lock, api_idx, prompt
        )
    
    def _get_legacy_mapping(self) -> Dict[str, tuple[QuestionType, SectionType]]:
        """
        Get mapping from legacy enum values to question/section types.
        
        Returns:
            Dictionary mapping legacy enum values to (QuestionType, SectionType)
        """
        return {
            # GMAT generators
            "Q_DS_gen": (QuestionType.DATA_SUFFICIENCY, SectionType.QUANTITATIVE),
            "Q_S_gen": (QuestionType.PROBLEM_SOLVING, SectionType.QUANTITATIVE),
            "V_PC_gen": (QuestionType.READING_COMPREHENSION, SectionType.VERBAL),
            "V_S_gen": (QuestionType.CRITICAL_REASONING, SectionType.VERBAL),
            "GI_gen": (QuestionType.GRAPHIC_INTERPRETATION, SectionType.INTEGRATED_REASONING),
            "TPA_gen": (QuestionType.TWO_PART_ANALYSIS, SectionType.INTEGRATED_REASONING),
            "TA_gen": (QuestionType.TABLE_ANALYSIS, SectionType.INTEGRATED_REASONING),
            "MSR_gen": (QuestionType.MULTI_SOURCE_REASONING, SectionType.INTEGRATED_REASONING),
            
            # GRE generators  
            "Q_PC_gen": (QuestionType.READING_COMPREHENSION, SectionType.QUANTITATIVE),
            "Q_NE_gen": (QuestionType.NUMERIC_ENTRY, SectionType.QUANTITATIVE),
            # Q_DS_gen and Q_S_gen are same as GMAT for GRE
            # V_PC_gen and V_S_gen are same as GMAT for GRE
        }


# Global factory instance
_factory_instance: Optional[QuestionGeneratorFactory] = None


def get_question_generator_factory() -> QuestionGeneratorFactory:
    """
    Get the global question generator factory instance.
    
    Returns:
        Singleton QuestionGeneratorFactory instance
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = QuestionGeneratorFactory()
    return _factory_instance