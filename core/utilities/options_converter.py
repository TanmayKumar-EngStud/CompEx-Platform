"""
Options Format Converter

This module provides utilities to convert between different option formats
used in the question generation system.

The AI models return options in dictionary format:
{
  "options": {"A": "option1", "B": "option2", "C": "option3"},
  "answer": "A"  # or ["A", "C"] for multiple answers
}

But the database and legacy code expect options in list format:
{
  "options": ["option1", "option2", "option3"],
  "answer": "option1"  # or ["option1", "option3"] for multiple answers
}

Author: Claude Code
Date: 2025-07-06
"""

from typing import Dict, List, Any, Union, Tuple


def convert_dict_options_to_list(
    options_dict: Dict[str, str], 
    answer_keys: Union[str, List[str]]
) -> Tuple[List[str], Union[str, List[str]]]:
    """
    Convert dictionary format options to list format.
    
    Args:
        options_dict: Dictionary with format {"A": "option1", "B": "option2", ...}
        answer_keys: Answer key(s) like "A" or ["A", "C"]
        
    Returns:
        Tuple of (options_list, answer_values)
        
    Example:
        options_dict = {"A": "option1", "B": "option2", "C": "option3"}
        answer_keys = "A"
        Returns: (["option1", "option2", "option3"], "option1")
        
        answer_keys = ["A", "C"]  
        Returns: (["option1", "option2", "option3"], ["option1", "option3"])
    """
    if not isinstance(options_dict, dict):
        raise ValueError(f"Expected dictionary for options_dict, got {type(options_dict)}")
    
    # Convert options to list (preserve order if possible)
    options_list = list(options_dict.values())
    
    # Convert answer keys to answer values
    if isinstance(answer_keys, str):
        # Single answer
        if answer_keys in options_dict:
            answer_values = options_dict[answer_keys]
        else:
            # Fallback to first option if key not found
            answer_values = options_list[0] if options_list else ""
    elif isinstance(answer_keys, list):
        # Multiple answers
        answer_values = []
        for key in answer_keys:
            if key in options_dict:
                answer_values.append(options_dict[key])
            elif options_list:
                # Fallback to first option if key not found
                answer_values.append(options_list[0])
    else:
        # Fallback case
        answer_values = options_list[0] if options_list else ""
    
    return options_list, answer_values


def convert_list_options_to_dict(
    options_list: List[str], 
    answer_values: Union[str, List[str]],
    start_letter: str = "A"
) -> Tuple[Dict[str, str], Union[str, List[str]]]:
    """
    Convert list format options to dictionary format.
    
    Args:
        options_list: List of option texts
        answer_values: Answer value(s) like "option1" or ["option1", "option3"]
        start_letter: Starting letter for keys (default "A")
        
    Returns:
        Tuple of (options_dict, answer_keys)
        
    Example:
        options_list = ["option1", "option2", "option3"]
        answer_values = "option1"
        Returns: ({"A": "option1", "B": "option2", "C": "option3"}, "A")
    """
    if not isinstance(options_list, list):
        raise ValueError(f"Expected list for options_list, got {type(options_list)}")
    
    # Convert list to dictionary
    options_dict = {}
    for i, option in enumerate(options_list):
        key = chr(ord(start_letter) + i)
        options_dict[key] = str(option)
    
    # Convert answer values to answer keys
    if isinstance(answer_values, str):
        # Single answer - find the key
        answer_keys = None
        for key, value in options_dict.items():
            if value == answer_values:
                answer_keys = key
                break
        if answer_keys is None:
            # Fallback to first key if value not found
            answer_keys = start_letter
    elif isinstance(answer_values, list):
        # Multiple answers - find the keys
        answer_keys = []
        for answer_value in answer_values:
            found_key = None
            for key, value in options_dict.items():
                if value == answer_value:
                    found_key = key
                    break
            if found_key:
                answer_keys.append(found_key)
            else:
                # Fallback to first key if value not found
                answer_keys.append(start_letter)
    else:
        # Fallback case
        answer_keys = start_letter
    
    return options_dict, answer_keys


def ensure_options_list_format(options: Any, answer: Any) -> Tuple[List[str], Any]:
    """
    Ensure options are in list format for database compatibility.
    
    Args:
        options: Options in any format (dict or list)
        answer: Answer in any format
        
    Returns:
        Tuple of (options_list, converted_answer)
    """
    if isinstance(options, dict):
        # Convert dictionary to list format
        options_list, converted_answer = convert_dict_options_to_list(options, answer)
        return options_list, converted_answer
    elif isinstance(options, list):
        # Already in list format
        return options, answer
    else:
        # Fallback - convert to list
        return [str(options)], str(answer)


def ensure_options_dict_format(options: Any, answer: Any) -> Tuple[Dict[str, str], Any]:
    """
    Ensure options are in dictionary format for AI compatibility.
    
    Args:
        options: Options in any format (dict or list)
        answer: Answer in any format
        
    Returns:
        Tuple of (options_dict, converted_answer)
    """
    if isinstance(options, dict):
        # Already in dictionary format
        return options, answer
    elif isinstance(options, list):
        # Convert list to dictionary format
        options_dict, converted_answer = convert_list_options_to_dict(options, answer)
        return options_dict, converted_answer
    else:
        # Fallback - create single-item dictionary
        options_dict = {"A": str(options)}
        return options_dict, "A"


def validate_options_format(options: Any, answer: Any) -> Tuple[bool, str]:
    """
    Validate options and answer format.
    
    Args:
        options: Options to validate
        answer: Answer to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if isinstance(options, dict):
        # Dictionary format validation
        if not options:
            return False, "Options dictionary is empty"
        
        # Check if all values are strings
        for key, value in options.items():
            if not isinstance(value, str):
                return False, f"Option value for key '{key}' is not a string: {type(value)}"
        
        # Check answer validity
        if isinstance(answer, str):
            if answer not in options:
                return False, f"Answer key '{answer}' not found in options"
        elif isinstance(answer, list):
            for ans in answer:
                if ans not in options:
                    return False, f"Answer key '{ans}' not found in options"
        
    elif isinstance(options, list):
        # List format validation
        if not options:
            return False, "Options list is empty"
        
        # Check if all items are strings
        for i, option in enumerate(options):
            if not isinstance(option, str):
                return False, f"Option at index {i} is not a string: {type(option)}"
        
        # Check answer validity
        if isinstance(answer, str):
            if answer not in options:
                return False, f"Answer value '{answer}' not found in options"
        elif isinstance(answer, list):
            for ans in answer:
                if ans not in options:
                    return False, f"Answer value '{ans}' not found in options"
    
    else:
        return False, f"Options must be dict or list, got {type(options)}"
    
    return True, "Valid format"