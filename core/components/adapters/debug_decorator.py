"""
Debug Logging Decorator for Adapter Methods

This module provides a decorator that logs function calls, instruction prompts,
and function returns to the system_instructions/in_the_run directory structure.

Author: Claude Code
Date: 2025-07-16
"""

import json
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType


class AdapterDebugLogger:
    """
    Debug logger for adapter methods that tracks function calls and their results.
    """
    
    def __init__(self):
        self.base_path = Path("system_instructions/in_the_run")
        self.call_counters = {}  # Track call priority index per exam/question type
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure debug directories exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "gmat").mkdir(exist_ok=True)
        (self.base_path / "gre").mkdir(exist_ok=True)
    
    def get_call_priority_index(self, exam_type: ExamType, question_type: QuestionType) -> int:
        """Get and increment call priority index for a specific exam/question type."""
        key = f"{exam_type.value}_{question_type.value}"
        if key not in self.call_counters:
            self.call_counters[key] = 0
        self.call_counters[key] += 1
        return self.call_counters[key]
    
    def log_function_call(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        function_name: str,
        instruction_prompt: str,
        function_return: Any,
        success: bool = True,
        error: Optional[str] = None
    ) -> str:
        """
        Log function call information to the debug system.
        
        Args:
            exam_type: GMAT or GRE
            question_type: Type of question being generated
            function_name: Name of the function being called
            instruction_prompt: The instruction prompt used
            function_return: The value returned by the function
            success: Whether the function call was successful
            error: Error message if any
            
        Returns:
            Path to the debug file created
        """
        # Get call priority index
        call_priority_index = self.get_call_priority_index(exam_type, question_type)
        
        # Create the debug directory structure
        exam_dir = self.base_path / exam_type.value.lower()
        question_style_dir = exam_dir / self._get_question_style_name(question_type)
        question_style_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with nomenclature: {idx}-{questionComponent}.json
        filename = f"{call_priority_index}-{function_name}.json"
        filepath = question_style_dir / filename
        
        # Prepare debug data
        debug_data = {
            "function_name": function_name,
            "instruction_prompt": instruction_prompt,
            "function_return": self._serialize_return_value(function_return),
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "call_priority_index": call_priority_index,
            "exam_type": exam_type.value,
            "question_type": question_type.value
        }
        
        # Write to file (overwrites existing file if same index)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _get_question_style_name(self, question_type: QuestionType) -> str:
        """Convert question type to question style directory name."""
        # Map question types to directory names
        style_mapping = {
            QuestionType.PROBLEM_SOLVING: "problem_solving",
            QuestionType.DATA_SUFFICIENCY: "data_sufficiency", 
            QuestionType.READING_COMPREHENSION: "reading_comprehension",
            QuestionType.CRITICAL_REASONING: "critical_reasoning",
            QuestionType.SENTENCE_CORRECTION: "sentence_correction",
            QuestionType.GRAPHIC_INTERPRETATION: "graphic_interpretation",
            QuestionType.TABLE_ANALYSIS: "table_analysis",
            QuestionType.TWO_PART_ANALYSIS: "two_part_analysis",
            QuestionType.MULTI_SOURCE_REASONING: "multi_source_reasoning",
            QuestionType.NUMERIC_ENTRY: "numeric_entry",
            QuestionType.TEXT_COMPLETION: "text_completion",
            QuestionType.SENTENCE_EQUIVALENCE: "sentence_equivalence",
            QuestionType.MULTIPLE_CHOICE_SINGLE: "multiple_choice_single",
            QuestionType.MULTIPLE_CHOICE_MULTIPLE: "multiple_choice_multiple",
            QuestionType.QUANTITATIVE_COMPARISON: "quantitative_comparison"
        }
        
        return style_mapping.get(question_type, question_type.value.lower())
    
    def _serialize_return_value(self, value: Any) -> str:
        """Serialize function return value for logging."""
        try:
            if value is None:
                return "None"
            elif isinstance(value, (str, int, float, bool)):
                return str(value)
            elif isinstance(value, (list, dict, tuple)):
                return json.dumps(value, ensure_ascii=False, default=str)
            else:
                return str(value)
        except Exception as e:
            return f"<Serialization Error: {str(e)}>"


# Global debug logger instance
_debug_logger = None


def get_debug_logger() -> AdapterDebugLogger:
    """Get the global debug logger instance."""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = AdapterDebugLogger()
    return _debug_logger


def debug_log_method(exam_type: ExamType, question_type: QuestionType):
    """
    Decorator to log adapter method calls with debug information.
    
    Args:
        exam_type: GMAT or GRE
        question_type: Type of question being generated
        
    Usage:
        @debug_log_method(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY)
        def generate_questionText(self):
            # method implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_debug_logger()
            function_name = func.__name__
            
            # We'll capture the actual instruction prompt by monkey-patching the component methods
            original_instruction_prompt = ""
            
            # Create a list to store the captured instruction prompt
            captured_prompts = []
            
            # Get the self object (adapter instance)
            adapter_self = args[0]
            
            # If this adapter has a component, we'll monkey-patch its generate methods
            if hasattr(adapter_self, 'component'):
                component = adapter_self.component
                
                # List of component methods that take instruction_prompt as first parameter
                component_methods = [
                    'generate_question_text', 'generate_question_title', 
                    'generate_question_solution', 'generate_question_options',
                    'generate_question_passage', 'generate_question_graph',
                    'generate_question_table', 'generate_question_metadata',
                    'generate_parent_title', 'generate_child_question',
                    'generate_child_options', 'generate_child_solution',
                    'generate_child_question_title', 'generate_source_info',
                    'generate_main_question_title', 'generate_parent_question_content',
                    'generate_question_options_with_answer'
                ]
                
                # Store original methods
                original_methods = {}
                
                # Monkey-patch each component method to capture instruction prompt
                for method_name in component_methods:
                    if hasattr(component, method_name):
                        original_method = getattr(component, method_name)
                        original_methods[method_name] = original_method
                        
                        def create_wrapper(orig_method, method_name):
                            def method_wrapper(*method_args, **method_kwargs):
                                # The first argument is usually the instruction prompt
                                if method_args and isinstance(method_args[0], str):
                                    captured_prompts.append(method_args[0])
                                return orig_method(*method_args, **method_kwargs)
                            return method_wrapper
                        
                        # Set the wrapped method
                        setattr(component, method_name, create_wrapper(original_method, method_name))
                
                try:
                    # Call the original function
                    result = func(*args, **kwargs)
                    
                    # Use the captured instruction prompt if available
                    if captured_prompts:
                        instruction_prompt = captured_prompts[0]  # Use the first captured prompt
                    else:
                        instruction_prompt = f"Function: {function_name}, Args: {str(args[1:])}, Kwargs: {str(kwargs)}"
                    
                    # Log successful function call
                    logger.log_function_call(
                        exam_type=exam_type,
                        question_type=question_type,
                        function_name=function_name,
                        instruction_prompt=instruction_prompt,
                        function_return=result,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    # Use the captured instruction prompt if available
                    if captured_prompts:
                        instruction_prompt = captured_prompts[0]
                    else:
                        instruction_prompt = f"Function: {function_name}, Args: {str(args[1:])}, Kwargs: {str(kwargs)}"
                    
                    # Log failed function call
                    logger.log_function_call(
                        exam_type=exam_type,
                        question_type=question_type,
                        function_name=function_name,
                        instruction_prompt=instruction_prompt,
                        function_return=None,
                        success=False,
                        error=str(e)
                    )
                    
                    # Re-raise the exception
                    raise
                
                finally:
                    # Restore original methods
                    for method_name, original_method in original_methods.items():
                        setattr(component, method_name, original_method)
            
            else:
                # Fallback for adapters without component
                try:
                    result = func(*args, **kwargs)
                    instruction_prompt = f"Function: {function_name}, Args: {str(args[1:])}, Kwargs: {str(kwargs)}"
                    
                    logger.log_function_call(
                        exam_type=exam_type,
                        question_type=question_type,
                        function_name=function_name,
                        instruction_prompt=instruction_prompt,
                        function_return=result,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    instruction_prompt = f"Function: {function_name}, Args: {str(args[1:])}, Kwargs: {str(kwargs)}"
                    
                    logger.log_function_call(
                        exam_type=exam_type,
                        question_type=question_type,
                        function_name=function_name,
                        instruction_prompt=instruction_prompt,
                        function_return=None,
                        success=False,
                        error=str(e)
                    )
                    
                    raise
        
        return wrapper
    return decorator


def reset_call_counters():
    """Reset call counters for a new session."""
    logger = get_debug_logger()
    logger.call_counters.clear()