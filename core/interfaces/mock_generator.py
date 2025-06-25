"""
Abstract interface for mock test generators.

This module defines the protocol that all mock generators must implement,
ensuring consistent behavior across different exam types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from ..enums.exam_types import ExamType
from ..enums.section_types import SectionType
from ..enums.difficulty_levels import DifficultyLevel


@runtime_checkable
class IMockGenerator(Protocol):
    """
    Protocol defining the interface for mock test generators.
    
    This protocol ensures that all mock generators implement
    the required methods for paper generation and management.
    """
    
    def generate_paper(self, difficulty: DifficultyLevel, is_mock: bool = True) -> Optional[Dict[str, Any]]:
        """
        Generate a complete exam paper.
        
        Args:
            difficulty: Target difficulty level for the paper
            is_mock: Whether this is a mock test or practice paper
            
        Returns:
            Dictionary containing the complete paper data, or None if generation fails
        """
        ...
    
    def generate_section(self, section_type: SectionType, 
                        difficulty: DifficultyLevel, 
                        question_count: int) -> Optional[List[Dict[str, Any]]]:
        """
        Generate questions for a specific section.
        
        Args:
            section_type: Type of section to generate
            difficulty: Target difficulty level
            question_count: Number of questions to generate
            
        Returns:
            List of question dictionaries, or None if generation fails
        """
        ...
    
    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator supports.
        
        Returns:
            Exam type enum value
        """
        ...
    
    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections supported by this exam type.
        
        Returns:
            List of supported section types
        """
        ...
    
    def validate_paper(self, paper_data: Dict[str, Any]) -> bool:
        """
        Validate the format and content of a generated paper.
        
        Args:
            paper_data: Generated paper data to validate
            
        Returns:
            True if the paper is valid, False otherwise
        """
        ...


class BaseMockGenerator(ABC):
    """
    Abstract base class for mock test generators.
    
    This class provides common functionality and enforces the implementation
    of required methods for all mock generators.
    """
    
    def __init__(self, exam_type: ExamType):
        """
        Initialize the base mock generator.
        
        Args:
            exam_type: The exam type this generator supports
        """
        self.exam_type = exam_type
        self.paper_counter = 0
    
    @abstractmethod
    def generate_paper(self, difficulty: DifficultyLevel, is_mock: bool = True) -> Optional[Dict[str, Any]]:
        """
        Generate a complete exam paper.
        
        This method must be implemented by concrete generator classes.
        
        Args:
            difficulty: Target difficulty level for the paper
            is_mock: Whether this is a mock test or practice paper
            
        Returns:
            Dictionary containing the complete paper data, or None if generation fails
        """
        pass
    
    @abstractmethod
    def generate_section(self, section_type: SectionType, 
                        difficulty: DifficultyLevel, 
                        question_count: int) -> Optional[List[Dict[str, Any]]]:
        """
        Generate questions for a specific section.
        
        This method must be implemented by concrete generator classes.
        
        Args:
            section_type: Type of section to generate
            difficulty: Target difficulty level
            question_count: Number of questions to generate
            
        Returns:
            List of question dictionaries, or None if generation fails
        """
        pass
    
    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator supports.
        
        Returns:
            Exam type enum value
        """
        return self.exam_type
    
    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections supported by this exam type.
        
        Returns:
            List of supported section types
        """
        return SectionType.get_supported_sections(self.exam_type)
    
    def validate_paper(self, paper_data: Dict[str, Any]) -> bool:
        """
        Validate the format and content of a generated paper.
        
        Args:
            paper_data: Generated paper data to validate
            
        Returns:
            True if the paper is valid, False otherwise
        """
        required_fields = ["exam_type", "difficulty", "sections", "total_questions", "generated_at"]
        
        for field in required_fields:
            if field not in paper_data:
                print(f"Missing required field in paper: {field}")
                return False
        
        # Validate exam type matches
        if paper_data.get("exam_type") != self.exam_type.value:
            print(f"Paper exam type mismatch: expected {self.exam_type.value}, got {paper_data.get('exam_type')}")
            return False
        
        # Validate sections
        sections = paper_data.get("sections", {})
        if not isinstance(sections, dict):
            print("Paper sections must be a dictionary")
            return False
        
        supported_sections = self.get_supported_sections()
        for section_name in sections.keys():
            try:
                section_type = SectionType.from_string(section_name)
                if section_type not in supported_sections:
                    print(f"Unsupported section for {self.exam_type.value}: {section_name}")
                    return False
            except ValueError:
                print(f"Invalid section name: {section_name}")
                return False
        
        return True
    
    def create_base_paper_structure(self, difficulty: DifficultyLevel, is_mock: bool) -> Dict[str, Any]:
        """
        Create a base paper structure with common metadata.
        
        Args:
            difficulty: Target difficulty level
            is_mock: Whether this is a mock test
            
        Returns:
            Dictionary with base paper structure
        """
        self.paper_counter += 1
        
        return {
            "exam_type": self.exam_type.value,
            "paper_id": f"{self.exam_type.value}_paper_{self.paper_counter}",
            "difficulty": difficulty.value,
            "is_mock": is_mock,
            "sections": {},
            "total_questions": 0,
            "generated_at": self._get_timestamp(),
            "metadata": {
                "generator_version": "1.0.0",
                "generation_method": "unified_system"
            }
        }
    
    def add_section_to_paper(self, paper_data: Dict[str, Any], 
                           section_type: SectionType, 
                           questions: List[Dict[str, Any]]) -> None:
        """
        Add a section and its questions to the paper.
        
        Args:
            paper_data: Paper data dictionary to modify
            section_type: Type of section being added
            questions: List of questions for this section
        """
        paper_data["sections"][section_type.value] = {
            "section_type": section_type.value,
            "question_count": len(questions),
            "questions": questions
        }
        
        paper_data["total_questions"] += len(questions)
    
    def get_section_question_counts(self) -> Dict[SectionType, int]:
        """
        Get the standard question counts for each section.
        
        This method should be overridden by specific exam implementations.
        
        Returns:
            Dictionary mapping section types to question counts
        """
        # Default implementation - should be overridden
        return {section: 10 for section in self.get_supported_sections()}
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp for paper generation tracking.
        
        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_paper(self, paper_data: Dict[str, Any], output_path: Optional[str] = None) -> bool:
        """
        Save the generated paper to a file.
        
        Args:
            paper_data: Paper data to save
            output_path: Optional custom output path
            
        Returns:
            True if saved successfully, False otherwise
        """
        from ..utilities.file_utils import save_json_file, get_papers_directory
        
        if output_path is None:
            papers_dir = get_papers_directory() / self.exam_type.value
            timestamp = paper_data.get("generated_at", "unknown").split("T")[0]
            difficulty = paper_data.get("difficulty", 1)
            filename = f"{self.exam_type.value}_paper-{timestamp}-difficulty-{difficulty}.json"
            output_path = papers_dir / filename
        
        return save_json_file(paper_data, output_path)


class IPromptGenerator(Protocol):
    """
    Protocol for generating prompts for different question types.
    """
    
    def generate_prompts(self, section_type: SectionType, 
                        difficulty: DifficultyLevel, 
                        question_count: int) -> List[str]:
        """
        Generate prompts for a section.
        
        Args:
            section_type: Type of section
            difficulty: Target difficulty level
            question_count: Number of prompts to generate
            
        Returns:
            List of prompt strings
        """
        ...
    
    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections this prompt generator supports.
        
        Returns:
            List of supported section types
        """
        ...


class BasePromptGenerator(ABC):
    """
    Abstract base class for prompt generators.
    """
    
    def __init__(self, exam_type: ExamType):
        """
        Initialize the prompt generator.
        
        Args:
            exam_type: The exam type this generator supports
        """
        self.exam_type = exam_type
    
    @abstractmethod
    def generate_prompts(self, section_type: SectionType, 
                        difficulty: DifficultyLevel, 
                        question_count: int) -> List[str]:
        """
        Generate prompts for a section.
        
        This method must be implemented by concrete generator classes.
        
        Args:
            section_type: Type of section
            difficulty: Target difficulty level
            question_count: Number of prompts to generate
            
        Returns:
            List of prompt strings
        """
        pass
    
    def get_supported_sections(self) -> List[SectionType]:
        """
        Get the sections this prompt generator supports.
        
        Returns:
            List of supported section types
        """
        return SectionType.get_supported_sections(self.exam_type)


# Type aliases for convenience
MockGeneratorType = IMockGenerator
PromptGeneratorType = IPromptGenerator