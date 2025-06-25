"""
Validation utility functions for the question generation system.

This module provides centralized validation capabilities for prompts,
question data, and other system inputs.
"""

import re
from typing import Dict, Any, List, Optional, Union
from ..enums.exam_types import ExamType
from ..enums.section_types import SectionType
from ..enums.question_types import QuestionType
from ..enums.difficulty_levels import DifficultyLevel


def validate_prompt(prompt: str) -> bool:
    """
    Validate a question generation prompt format.
    
    Args:
        prompt: Prompt string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not prompt or not isinstance(prompt, str):
        return False
    
    # Basic length check
    if len(prompt.strip()) < 5 or len(prompt) > 1000:
        return False
    
    # Check for reasonable content (contains letters and some structure)
    if not re.search(r'[a-zA-Z]', prompt):
        return False
    
    return True


def validate_difficulty_level(difficulty: Union[int, str, DifficultyLevel]) -> bool:
    """
    Validate difficulty level input.
    
    Args:
        difficulty: Difficulty level to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(difficulty, DifficultyLevel):
            return True
        elif isinstance(difficulty, int):
            return 1 <= difficulty <= 5
        elif isinstance(difficulty, str):
            DifficultyLevel.from_string(difficulty)
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def validate_exam_type(exam_type: Union[str, ExamType]) -> bool:
    """
    Validate exam type input.
    
    Args:
        exam_type: Exam type to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(exam_type, ExamType):
            return True
        elif isinstance(exam_type, str):
            ExamType.from_string(exam_type)
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def validate_question_type(question_type: Union[str, QuestionType]) -> bool:
    """
    Validate question type input.
    
    Args:
        question_type: Question type to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(question_type, QuestionType):
            return True
        elif isinstance(question_type, str):
            QuestionType.from_string(question_type)
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def validate_section_type(section_type: Union[str, SectionType]) -> bool:
    """
    Validate section type input.
    
    Args:
        section_type: Section type to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(section_type, SectionType):
            return True
        elif isinstance(section_type, str):
            SectionType.from_string(section_type)
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def validate_question_data(question_data: Dict[str, Any], 
                          question_type: Optional[QuestionType] = None) -> bool:
    """
    Validate question data structure.
    
    Args:
        question_data: Question data dictionary to validate
        question_type: Expected question type for additional validation
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(question_data, dict):
        return False
    
    # Required fields for all questions
    required_fields = ["type", "content", "question", "answer", "solution", "difficulty"]
    
    for field in required_fields:
        if field not in question_data:
            print(f"Missing required field: {field}")
            return False
    
    # Validate difficulty
    if not validate_difficulty_level(question_data.get("difficulty")):
        print(f"Invalid difficulty level: {question_data.get('difficulty')}")
        return False
    
    # Type-specific validation
    if question_type:
        if not _validate_type_specific_content(question_data, question_type):
            return False
    
    return True


def _validate_type_specific_content(question_data: Dict[str, Any], 
                                   question_type: QuestionType) -> bool:
    """
    Validate question data based on specific question type requirements.
    
    Args:
        question_data: Question data to validate
        question_type: Question type for validation rules
        
    Returns:
        True if valid, False otherwise
    """
    content = question_data.get("content", {})
    
    if question_type == QuestionType.DATA_SUFFICIENCY:
        # Data sufficiency questions need passages and statements
        required_ds_fields = ["passages", "statements"]
        for field in required_ds_fields:
            if field not in content:
                print(f"Data sufficiency question missing: {field}")
                return False
        
        # Statements should be a list with exactly 2 items
        statements = content.get("statements")
        if not isinstance(statements, list) or len(statements) != 2:
            print("Data sufficiency questions must have exactly 2 statements")
            return False
    
    elif question_type == QuestionType.READING_COMPREHENSION:
        # Reading comprehension questions need passages
        if "passages" not in content and "passage" not in content:
            print("Reading comprehension question missing passage")
            return False
    
    elif question_type in [QuestionType.GRAPHIC_INTERPRETATION, 
                          QuestionType.TABLE_ANALYSIS,
                          QuestionType.MULTI_SOURCE_REASONING]:
        # IR questions typically need specialized content
        if not content or len(content) == 0:
            print(f"{question_type.value} question missing specialized content")
            return False
    
    return True


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(api_key, str):
        return False
    
    # Basic validation for Google Gemini API keys
    if len(api_key) < 20:
        return False
    
    # Check for reasonable characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False
    
    return True


def validate_file_path(file_path: str, must_exist: bool = False) -> bool:
    """
    Validate file path format and optionally check existence.
    
    Args:
        file_path: File path to validate
        must_exist: Whether the file must exist
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(file_path, str) or not file_path.strip():
        return False
    
    # Check for dangerous path patterns
    dangerous_patterns = ['..', '//', '\\\\', '<', '>', '|', '*', '?']
    for pattern in dangerous_patterns:
        if pattern in file_path:
            return False
    
    if must_exist:
        import os
        return os.path.exists(file_path)
    
    return True


def sanitize_input_string(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize input string by removing potentially harmful content.
    
    Args:
        input_string: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(input_string, str):
        return ""
    
    # Truncate if too long
    if len(input_string) > max_length:
        input_string = input_string[:max_length]
    
    # Remove potentially harmful characters but keep essential punctuation
    # Allow letters, numbers, spaces, and basic punctuation
    sanitized = re.sub(r'[^\w\s\-.,;:!?()[\]{}"\'/\\<>]', '', input_string)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def validate_question_options(options: List[str], answer: str) -> bool:
    """
    Validate question options and answer.
    
    Args:
        options: List of option strings
        answer: Correct answer
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(options, list) or len(options) < 2:
        print("Options must be a list with at least 2 items")
        return False
    
    if not isinstance(answer, str) or not answer.strip():
        print("Answer must be a non-empty string")
        return False
    
    # Check if answer corresponds to an option (for MCQ questions)
    if answer not in options and not _is_valid_option_label(answer, len(options)):
        print(f"Answer '{answer}' does not match any option or valid label")
        return False
    
    return True


def _is_valid_option_label(label: str, num_options: int) -> bool:
    """
    Check if a label is a valid option identifier (A, B, C, etc.).
    
    Args:
        label: Label to check
        num_options: Number of options available
        
    Returns:
        True if valid label, False otherwise
    """
    if len(label) == 1 and label.upper() in 'ABCDEFGHIJ'[:num_options]:
        return True
    
    # Check for numeric labels (1, 2, 3, etc.)
    try:
        num = int(label)
        return 1 <= num <= num_options
    except ValueError:
        return False


def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate that a JSON structure contains required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        
    Returns:
        True if all required keys are present, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        print(f"Missing required keys: {missing_keys}")
        return False
    
    return True