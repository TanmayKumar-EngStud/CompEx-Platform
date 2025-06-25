"""
Abstract interface for question generators.

This module defines the protocol that all question generators must implement,
ensuring consistent behavior across different question types and exam formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol, runtime_checkable
from ..enums.exam_types import ExamType
from ..enums.question_types import QuestionType
from ..enums.difficulty_levels import DifficultyLevel


@runtime_checkable
class IQuestionGenerator(Protocol):
    """
    Protocol defining the interface for question generators.
    
    This protocol ensures that all question generators implement
    the required methods for question generation and validation.
    """
    
    def generate_question(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate a single question based on the provided prompt.
        
        Args:
            prompt: The input prompt for question generation
            
        Returns:
            Dictionary containing the generated question data, or None if generation fails
            
        The returned dictionary should contain at minimum:
        - type: Question type classification
        - content: Question content and data
        - question: The main question text
        - answer: The correct answer
        - solution: Detailed solution explanation
        - difficulty: Numerical difficulty level (1-5)
        - tags: List of relevant topic tags
        """
        ...
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate the format and content of generated question data.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if the question data is valid, False otherwise
        """
        ...
    
    def get_supported_types(self) -> list[QuestionType]:
        """
        Get the question types supported by this generator.
        
        Returns:
            List of supported question types
        """
        ...
    
    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator is designed for.
        
        Returns:
            Exam type enum value
        """
        ...


class BaseQuestionGenerator(ABC):
    """
    Abstract base class for question generators.
    
    This class provides common functionality and enforces the implementation
    of required methods for all question generators.
    """
    
    def __init__(self, exam_type: ExamType, question_type: QuestionType):
        """
        Initialize the base question generator.
        
        Args:
            exam_type: The exam type this generator supports
            question_type: The primary question type this generator creates
        """
        self.exam_type = exam_type
        self.question_type = question_type
        self.max_retries = 3
    
    @abstractmethod
    def generate_question(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate a single question based on the provided prompt.
        
        This method must be implemented by concrete generator classes.
        
        Args:
            prompt: The input prompt for question generation
            
        Returns:
            Dictionary containing the generated question data, or None if generation fails
        """
        pass
    
    @abstractmethod
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate the format and content of generated question data.
        
        This method must be implemented by concrete generator classes.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if the question data is valid, False otherwise
        """
        pass
    
    def get_supported_types(self) -> list[QuestionType]:
        """
        Get the question types supported by this generator.
        
        Returns:
            List containing the primary question type
        """
        return [self.question_type]
    
    def get_exam_type(self) -> ExamType:
        """
        Get the exam type this generator is designed for.
        
        Returns:
            Exam type enum value
        """
        return self.exam_type
    
    def extract_difficulty_from_prompt(self, prompt: str) -> DifficultyLevel:
        """
        Extract difficulty level from prompt string.
        
        Args:
            prompt: Prompt string containing difficulty information
            
        Returns:
            Difficulty level enum value, defaults to MEDIUM if not found
        """
        import re
        
        # Look for difficulty patterns in the prompt
        difficulty_patterns = [
            r'difficulty[_\s]*level[:\s]*(\d+)',
            r'difficulty[:\s]*(\d+)',
            r'level[:\s]*(\d+)'
        ]
        
        for pattern in difficulty_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                try:
                    return DifficultyLevel.from_int(int(match.group(1)))
                except ValueError:
                    continue
        
        # Default to medium difficulty
        return DifficultyLevel.MEDIUM
    
    def create_base_question_structure(self, prompt: str) -> Dict[str, Any]:
        """
        Create a base question structure with common fields.
        
        Args:
            prompt: Original prompt used for generation
            
        Returns:
            Dictionary with base question structure
        """
        return {
            "type": self.question_type.value,
            "prompt": prompt,
            "content": {},
            "question": "",
            "title": "",
            "options": [],
            "answer": "",
            "solution": "",
            "difficulty": self.extract_difficulty_from_prompt(prompt).value,
            "tags": [],
            "exam_type": self.exam_type.value,
            "generated_at": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp for question generation tracking.
        
        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries failed
        """
        import time
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    return result
                
                print(f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
                
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")
                
                # Wait before retry with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # If we get here, all attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        
        return None


class IMultiPartQuestionGenerator(Protocol):
    """
    Protocol for generators that create multi-part questions (like parent-child questions).
    """
    
    def generate_parent_content(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate the parent/shared content for multi-part questions.
        
        Args:
            prompt: The input prompt for content generation
            
        Returns:
            Dictionary containing parent content, or None if generation fails
        """
        ...
    
    def generate_child_question(self, parent_content: Dict[str, Any], 
                               child_index: int, child_prompt: str = "") -> Optional[Dict[str, Any]]:
        """
        Generate a child question based on parent content.
        
        Args:
            parent_content: Previously generated parent content
            child_index: Index of the child question (0-based)
            child_prompt: Optional specific prompt for this child question
            
        Returns:
            Dictionary containing child question data, or None if generation fails
        """
        ...
    
    def get_child_question_count(self, prompt: str) -> int:
        """
        Determine how many child questions should be generated.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Number of child questions to generate
        """
        ...


class ISpecializedQuestionGenerator(Protocol):
    """
    Protocol for generators that create specialized questions (like Integrated Reasoning).
    """
    
    def generate_specialized_content(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate specialized content (charts, tables, etc.) for the question.
        
        Args:
            prompt: The input prompt for content generation
            
        Returns:
            Dictionary containing specialized content, or None if generation fails
        """
        ...
    
    def get_content_type(self) -> str:
        """
        Get the type of specialized content this generator creates.
        
        Returns:
            String describing the content type (e.g., "chart", "table", "graph")
        """
        ...


# Type aliases for convenience
QuestionGeneratorType = IQuestionGenerator
MultiPartGeneratorType = IMultiPartQuestionGenerator
SpecializedGeneratorType = ISpecializedQuestionGenerator