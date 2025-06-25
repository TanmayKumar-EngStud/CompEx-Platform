"""
Unified Question Components Module

This module provides unified question generation components that eliminate code duplication
across GMAT and GRE sections. All question generation classes inherit from base components
that provide common functionality while maintaining exam-specific behaviors through adapters.

Classes:
    BaseQuestionComponent: Abstract base class for all question components
    SimpleQuestion: Unified simple question generation
    DataSufficiencyQuestion: Unified data sufficiency question generation  
    ParentChildQuestion: Unified parent-child question generation
    SpecializedQuestion: Base for specialized IR questions
    GraphicInterpretationQuestion: Unified GI question generation
    TableAnalysisQuestion: Unified TA question generation
    TwoPartAnalysisQuestion: Unified TPA question generation
    MultiSourceReasoningQuestion: Unified MSR question generation

Author: Claude Code (Migration CHUNK 2)
Date: 2025-06-25
"""

import json
import re
import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from google import genai
from google.genai import types

# Import core utilities created in CHUNK 1
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.difficulty_levels import DifficultyLevel
from core.utilities.json_utils import refine_response
from core.utilities.validation_utils import validate_prompt
# Define exception locally since core.exceptions module doesn't exist yet
class QuestionGenerationException(Exception):
    """Raised when question generation fails."""
    pass

# Global constants
WARNING_MESSAGE = "\nCRITICAL ERROR: Your response MUST be valid JSON only. EXAMPLE: {\"solution\": \"text here\"}. No text before/after JSON. No explanations. No markdown. Just pure JSON that can be parsed by json.loads(). Use (`) instead of single quotes inside strings."
MAX_RETRIES = 3
RATE_LIMIT_REQUESTS_PER_MINUTE = 9  # Use 9 instead of 10 for safety margin
RATE_LIMIT_WINDOW_SECONDS = 60


def is_error_response(message: Dict[str, Any]) -> bool:
    """Check if the parsed JSON is an error response from refine_response."""
    return isinstance(message, dict) and "error" in message and len(message) == 1


def log_detailed_error(context: str, raw_response: str, error: str, expected_keys: Optional[List[str]] = None) -> None:
    """Log detailed error information for debugging."""
    print("=" * 80)
    print(f"DETAILED ERROR LOG - {context}")
    print("=" * 80)
    print(f"Error: {error}")
    print("-" * 40)
    print("RAW RESPONSE:")
    print(raw_response)
    print("-" * 40)
    print(f"Response type: {type(raw_response)}")
    print(f"Response length: {len(raw_response) if raw_response else 0}")
    if expected_keys:
        print(f"Expected keys: {expected_keys}")
    print("=" * 80)
    print()


class BaseQuestionComponent(ABC):
    """
    Abstract base class for all question generation components.
    
    Provides common functionality including:
    - Rate limiting and API management
    - Retry logic with exponential backoff
    - Error handling and logging
    - Response processing and validation
    
    All specific question types inherit from this class to ensure consistency.
    """
    
    def __init__(
        self, 
        llm: genai.Client,
        system_instructions: str,
        global_state: Dict[str, Any],
        lock: Any,
        prompt: str,
        exam_type: ExamType = ExamType.GMAT,
        question_type: Optional[QuestionType] = None
    ):
        """
        Initialize the base question component.
        
        Args:
            llm: Google Generative AI client
            system_instructions: AI system instruction text
            global_state: Shared state for rate limiting
            lock: Thread lock for rate limiting
            prompt: Question generation prompt
            exam_type: Target exam type (GMAT or GRE)
            question_type: Specific question type being generated
        """
        self.llm = llm
        self.system_instructions = system_instructions
        self.global_state = global_state
        self.lock = lock
        self.prompt = prompt
        self.exam_type = exam_type
        self.question_type = question_type
        self.max_retries = MAX_RETRIES
        
        # Validate prompt
        if not validate_prompt(prompt):
            raise QuestionGenerationException(f"Invalid prompt format: {prompt}")
        
        # Create chat session
        self.chat = self._create_chat_session()
    
    def _create_chat_session(self) -> Any:
        """Create a chat session with appropriate configuration."""
        config = types.GenerateContentConfig(
            system_instruction=self.system_instructions
        )
        
        # Add thinking config for certain question types that benefit from it
        thinking_types = {
            QuestionType.DATA_SUFFICIENCY,
            QuestionType.GRAPHIC_INTERPRETATION,
            QuestionType.READING_COMPREHENSION
        }
        
        if self.question_type in thinking_types:
            config.thinking_config = types.ThinkingConfig(include_thoughts=True)
        
        return self.llm.chats.create(
            model=os.getenv("MODEL", "gemini-1.5-pro"),
            config=config
        )
    
    def _get_response(self, prompt: str, warn: bool = False) -> Optional[str]:
        """
        Get response from AI with rate limiting and error handling.
        
        Args:
            prompt: The prompt to send to AI
            warn: Whether to append warning message
            
        Returns:
            AI response text or None if failed
        """
        if warn:
            prompt += WARNING_MESSAGE
        
        # Rate limiting logic
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.global_state["start_time"]
            
            # Reset window if more than 60 seconds have passed
            if elapsed >= RATE_LIMIT_WINDOW_SECONDS:
                self.global_state["start_time"] = current_time
                self.global_state["request_count"] = 0
                elapsed = 0
            
            # Check if we're at the limit
            if self.global_state["request_count"] >= RATE_LIMIT_REQUESTS_PER_MINUTE:
                wait_time = RATE_LIMIT_WINDOW_SECONDS - elapsed + 1  # Add buffer
                if wait_time > 0:
                    print(f"Rate limit safety: waiting {wait_time:.1f}s "
                          f"(requests: {self.global_state['request_count']}, "
                          f"elapsed: {elapsed:.1f}s)")
                    time.sleep(wait_time)
                    # Reset after waiting
                    self.global_state["start_time"] = time.time()
                    self.global_state["request_count"] = 0
            
            # Increment request count
            self.global_state["request_count"] += 1
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Failed to generate response for prompt: {prompt}")
            print(f"Error: {str(e)}")
            
            # On error, wait longer before retry
            with self.lock:
                current_time = time.time()
                elapsed = current_time - self.global_state["start_time"]
                if elapsed < RATE_LIMIT_WINDOW_SECONDS:
                    wait_time = RATE_LIMIT_WINDOW_SECONDS - elapsed + 2  # Extra buffer
                    time.sleep(wait_time)
                self.global_state["start_time"] = time.time()
                self.global_state["request_count"] = 0
            return None
    
    def _retry_generate(self, func, *args, **kwargs) -> Any:
        """
        Retry a generation function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all attempts failed
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Add warn parameter for retries
                result = func(*args, warn=(attempt > 0), **kwargs)
                if result is not None:  # Accept any non-None result
                    return result
                print(f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"Error in attempt {attempt + 1}: {last_error}")
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # All attempts failed
        if last_error:
            print(f"All attempts failed. Last error: {last_error}")
        return None
    
    def _process_json_response(
        self, 
        response: str, 
        expected_keys: List[str],
        context: str = "generation"
    ) -> Optional[Dict[str, Any]]:
        """
        Process JSON response with error handling.
        
        Args:
            response: Raw AI response
            expected_keys: List of expected JSON keys
            context: Context for error logging
            
        Returns:
            Parsed JSON dict or None if failed
        """
        try:
            refined = refine_response(response)
            message = json.loads(refined)
            
            # Check if this is an error response
            if is_error_response(message):
                log_detailed_error(
                    f"{self.exam_type.value} {context} - JSON parsing failed",
                    response,
                    f"refine_response returned error: {message.get('error', 'Unknown error')}",
                    expected_keys
                )
                return None
            
            return message
            
        except Exception as e:
            log_detailed_error(
                f"{self.exam_type.value} {context} - Exception during parsing",
                response,
                str(e),
                expected_keys
            )
            return None
    
    @abstractmethod
    def generate_question_text(self, *args, **kwargs) -> Any:
        """Generate question text. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def generate_question_title(self, *args, **kwargs) -> Any:
        """Generate question title. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def generate_question_solution(self, *args, **kwargs) -> Any:
        """Generate question solution. Must be implemented by subclasses."""
        pass


class SimpleQuestion(BaseQuestionComponent):
    """
    Unified simple question generation component.
    
    Handles single-part questions for both GMAT and GRE, including:
    - Standard multiple choice questions
    - Numeric entry questions (GRE only)
    - Critical reasoning questions
    - Text completion questions
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize simple question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.PROBLEM_SOLVING  # Default
    
    def generate_question_text(self, input_data: Optional[str] = None) -> str:
        """
        Generate question text.
        
        Args:
            input_data: Optional input data for question generation
            
        Returns:
            Generated question text
        """
        def _generate(warn: bool = False) -> Optional[str]:
            prompt_text = f"QuestionText: {input_data or self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response, 
                ["question"], 
                "SimpleQuestion generate_question_text"
            )
            
            if message and message.get("question"):
                return message["question"]
            return None
        
        result = self._retry_generate(_generate)
        return result if result else "Error generating question text"
    
    def generate_question_title(self) -> str:
        """Generate question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionTitle", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "SimpleQuestion generate_question_title"
            )
            
            if message:
                return message.get("title", "")
            return None
        
        result = self._retry_generate(_generate)
        return result if result else ""
    
    def generate_question_solution(self, is_numeric_entry: bool = False) -> Union[str, Tuple[str, float]]:
        """
        Generate question solution.
        
        Args:
            is_numeric_entry: Whether this is a numeric entry question (GRE only)
            
        Returns:
            Solution string for MCQ, or (solution, answer) tuple for numeric entry
        """
        def _generate(warn: bool = False) -> Optional[Union[str, Tuple[str, float]]]:
            response = self._get_response("QuestionSolution", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution", "answer"] if is_numeric_entry else ["solution"],
                "SimpleQuestion generate_question_solution"
            )
            
            if not message:
                return None
            
            if is_numeric_entry:
                solution = message.get("solution", "")
                answer = message.get("answer")
                if answer is not None:
                    try:
                        return solution, float(answer)
                    except (ValueError, TypeError):
                        print(f"Warning: Could not convert answer to float: {answer}")
                        return solution, 0.0
                return solution, 0.0
            else:
                return message.get("solution", "")
        
        result = self._retry_generate(_generate)
        
        if is_numeric_entry:
            if result is None:
                return "", 0.0
            return result
        else:
            return result if result else ""
    
    def generate_question_options(self) -> Tuple[List[str], str]:
        """
        Generate question options and correct answer.
        
        Returns:
            Tuple of (options_list, correct_answer)
        """
        def _generate(warn: bool = False) -> Optional[Tuple[List[str], str]]:
            response = self._get_response("QuestionOptions", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"],
                "SimpleQuestion generate_question_options"
            )
            
            if message and message.get("options") and message.get("answer"):
                return message["options"], message["answer"]
            return None
        
        result = self._retry_generate(_generate)
        return result if result else ([], "")


class DataSufficiencyQuestion(BaseQuestionComponent):
    """
    Unified data sufficiency question generation component.
    
    Handles data sufficiency questions for both GMAT and GRE with:
    - Question passage generation
    - Two statement generation
    - Standard DS answer options
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize data sufficiency question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.DATA_SUFFICIENCY
    
    def generate_question_graph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph/table if needed."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"questionGraph: {self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["graph/table", "graph"],
                "DataSufficiencyQuestion generate_question_graph"
            )
            
            if message:
                # Try different possible keys
                return (message.get("graph/table") or 
                       message.get("graph") or 
                       message.get("table"))
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_text(self) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """
        Generate question text components.
        
        Returns:
            Tuple of (passage, statements_list, question)
        """
        def _generate(warn: bool = False) -> Optional[Tuple[str, List[str], str]]:
            prompt_text = f"QuestionText: {self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            # Different key patterns for GMAT vs GRE
            if self.exam_type == ExamType.GMAT:
                expected_keys = ["question_passage", "statements", "question"]
            else:  # GRE
                expected_keys = ["passage", "statements", "question"]
            
            message = self._process_json_response(
                response,
                expected_keys,
                "DataSufficiencyQuestion generate_question_text"
            )
            
            if not message:
                return None
            
            # Extract components based on exam type
            if self.exam_type == ExamType.GMAT:
                passage = message.get("question_passage")
                statements = message.get("statements")
                question = message.get("question")
            else:  # GRE
                passage = message.get("passage")
                statements = message.get("statements")
                question = message.get("question")
            
            if passage and statements and question:
                return passage, statements, question
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None, None
        return result
    
    def generate_question_title(self) -> Optional[str]:
        """Generate question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionTitle", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "DataSufficiencyQuestion generate_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_solution(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate question solution and answer.
        
        Returns:
            Tuple of (solution, answer)
        """
        def _generate(warn: bool = False) -> Optional[Tuple[str, str]]:
            response = self._get_response("questionSolution", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution", "answer"],
                "DataSufficiencyQuestion generate_question_solution"
            )
            
            if message and message.get("solution") and message.get("answer"):
                return message["solution"], str(message["answer"])
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        return result
    
    def generate_question_options(self) -> Tuple[List[str], str]:
        """
        Generate standard DS options and answer.
        
        Returns:
            Tuple of (standard_ds_options, correct_answer)
        """
        # Standard data sufficiency options
        standard_options = [
            "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.",
            "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient.", 
            "BOTH statements TOGETHER are sufficient, but NEITHER statement ALONE is sufficient.",
            "EACH statement ALONE is sufficient.",
            "Statements (1) and (2) TOGETHER are NOT sufficient."
        ]
        
        def _generate(warn: bool = False) -> Optional[Tuple[List[str], str]]:
            response = self._get_response("QuestionOptions", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"],
                "DataSufficiencyQuestion generate_question_options"
            )
            
            if message and message.get("answer"):
                return standard_options, str(message["answer"])
            return None
        
        result = self._retry_generate(_generate)
        return result if result else (standard_options, "A")


class ParentChildQuestion(BaseQuestionComponent):
    """
    Unified parent-child question generation component.
    
    Handles multi-part questions with shared content:
    - Reading comprehension questions
    - Problem-solving with shared graphs/tables
    - Multi-source reasoning child questions
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize parent-child question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.READING_COMPREHENSION  # Default
    
    def generate_question_graph(self) -> Optional[Dict[str, Any]]:
        """Generate shared graph/table for child questions."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"questionGraph: {self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["graph/table", "graph"],
                "ParentChildQuestion generate_question_graph"
            )
            
            if message:
                # Try different possible keys
                graph = message.get("graph/table") or message.get("graph")
                if graph is None and "graph" not in message and "graph/table" not in message:
                    print(f"Warning: Expected 'graph' or 'graph/table' key, got: {list(message.keys())}")
                return graph
            return None
        
        return self._retry_generate(_generate)
    
    def generate_parent_title(self) -> Optional[str]:
        """Generate title for parent question set."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("ParentTitle", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "ParentChildQuestion generate_parent_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_child_question_title(self, index: int) -> Optional[str]:
        """Generate title for specific child question."""
        def _generate(warn: bool = False) -> Optional[str]:
            prompt_text = f"ChildQuestionTitle: {index}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                f"ParentChildQuestion generate_child_question_title {index}"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_child_question(self, index: int, child_prompt: str = "") -> Optional[str]:
        """Generate specific child question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            prompt_text = f"generate ChildQuestion: {index} of {child_prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["question"],
                f"ParentChildQuestion generate_child_question {index}"
            )
            
            if message:
                return message.get("question")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_child_options(self, index: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate options and answer for specific child question."""
        def _generate(warn: bool = False) -> Optional[Tuple[List[str], str]]:
            prompt_text = f"ChildOptions: {index}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"],
                f"ParentChildQuestion generate_child_options {index}"
            )
            
            if message and message.get("options") and message.get("answer"):
                return message["options"], message["answer"]
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        return result
    
    def generate_child_solution(self, index: int) -> Optional[str]:
        """Generate solution for specific child question."""
        def _generate(warn: bool = False) -> Optional[str]:
            prompt_text = f"mode:- childQuestionSolution; question: {index}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution"],
                f"ParentChildQuestion generate_child_solution {index}"
            )
            
            if message:
                return message.get("solution")
            return None
        
        return self._retry_generate(_generate)
    
    # Required abstract method implementations
    def generate_question_text(self, *args, **kwargs) -> Any:
        """Generate question text - delegates to child question generation."""
        return self.generate_child_question(*args, **kwargs)
    
    def generate_question_title(self, *args, **kwargs) -> Any:
        """Generate question title - delegates to parent title generation."""
        return self.generate_parent_title(*args, **kwargs)
    
    def generate_question_solution(self, *args, **kwargs) -> Any:
        """Generate question solution - delegates to child solution generation."""
        return self.generate_child_solution(*args, **kwargs)


# Specialized IR Question Components (GMAT only)

class SpecializedQuestion(BaseQuestionComponent):
    """Base class for specialized integrated reasoning questions."""
    
    def __init__(self, *args, **kwargs):
        """Initialize specialized question component."""
        super().__init__(*args, **kwargs)
        if self.exam_type != ExamType.GMAT:
            raise QuestionGenerationException(
                f"Specialized questions are only available for GMAT, not {self.exam_type.value}"
            )


class GraphicInterpretationQuestion(SpecializedQuestion):
    """Unified graphic interpretation question component (GMAT only)."""
    
    def __init__(self, *args, **kwargs):
        """Initialize GI question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.GRAPHIC_INTERPRETATION
    
    def generate_question_graph(self) -> Optional[Dict[str, Any]]:
        """Generate graph/chart for GI question."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"Mode: QuestionGraph\nPrompt: {self.prompt}\nreturn: `graph`"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["graph"],
                "GraphicInterpretationQuestion generate_question_graph"
            )
            
            return message
        
        return self._retry_generate(_generate)
    
    def generate_question_text(self) -> Optional[str]:
        """Generate GI question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("Mode: QuestionText return: `question`", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["question"],
                "GraphicInterpretationQuestion generate_question_text"
            )
            
            if message:
                return message.get("question")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_title(self) -> Optional[str]:
        """Generate GI question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("Mode: QuestionTitle return: `title`", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "GraphicInterpretationQuestion generate_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_solution(self) -> Optional[str]:
        """Generate GI question solution."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("Mode: QuestionSolution return: `solution`", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution", "answer", "explanation", "question"],
                "GraphicInterpretationQuestion generate_question_solution"
            )
            
            if message:
                # Try different possible solution keys
                return (message.get("solution") or 
                       message.get("answer") or 
                       message.get("explanation") or 
                       message.get("question"))
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_options(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate GI question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response("Mode: QuestionOptions return: `options`, `answer`", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"],
                "GraphicInterpretationQuestion generate_question_options"
            )
            
            if message:
                # Try different possible keys for options and answers
                options = (message.get("options") or 
                          message.get("choices") or 
                          message.get("solution"))
                
                answers = (message.get("answer") or 
                          message.get("answers") or 
                          (message.get("solution") if options != message.get("solution") else None))
                
                if options is not None and answers is not None:
                    return options, answers
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        return result


class TableAnalysisQuestion(SpecializedQuestion):
    """Unified table analysis question component (GMAT only)."""
    
    def __init__(self, *args, **kwargs):
        """Initialize TA question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.TABLE_ANALYSIS
        self.temp_data = None
    
    def generate_question_table(self, num_rows: int, num_cols: int) -> Optional[Dict[str, Any]]:
        """Generate table for TA question."""
        self.temp_data = [num_rows, num_cols]
        
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"QuestionTable, no_rows: {num_rows}, no_cols: {num_cols}; InputPrompt: {self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["tables", "content", "table"],
                "TableAnalysisQuestion generate_question_table"
            )
            
            if message:
                return (message.get("tables") or 
                       message.get("content") or 
                       message.get("table"))
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_text(self) -> Optional[str]:
        """Generate TA question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionText", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["question", "text", "content", "title"],
                "TableAnalysisQuestion generate_question_text"
            )
            
            if message:
                return (message.get("question") or 
                       message.get("text") or 
                       message.get("content") or 
                       message.get("title"))
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_title(self) -> Optional[str]:
        """Generate TA question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionTitle", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "TableAnalysisQuestion generate_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_solution(self) -> Optional[str]:
        """Generate TA question solution."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionSolution", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution"],
                "TableAnalysisQuestion generate_question_solution"
            )
            
            if message:
                return message.get("solution")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_options(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate TA question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response("QuestionOptions", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer", "choices", "answers"],
                "TableAnalysisQuestion generate_question_options"
            )
            
            if message:
                # Try different possible keys for options and answers
                options = (message.get("options") or 
                          message.get("choices") or 
                          message.get("question"))
                
                answers = (message.get("answer") or 
                          message.get("answers") or 
                          message.get("solution"))
                
                if options is not None and answers is not None:
                    return options, answers
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        return result


class TwoPartAnalysisQuestion(SpecializedQuestion):
    """Unified two-part analysis question component (GMAT only)."""
    
    def __init__(self, *args, **kwargs):
        """Initialize TPA question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.TWO_PART_ANALYSIS
    
    def generate_parent_question_content(self) -> Optional[Dict[str, Any]]:
        """Generate shared content for TPA questions."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"ParentQuestionContent: {self.prompt}"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["content", "question", "graph", "data"],
                "TwoPartAnalysisQuestion generate_parent_question_content"
            )
            
            if message:
                return (message.get("content") or 
                       message.get("question") or 
                       message.get("graph") or 
                       message.get("data"))
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_text(self, difficulties: List[int]) -> List[str]:
        """Generate TPA question texts with different difficulties."""
        def _generate(warn: bool = False) -> Optional[List[str]]:
            questions = []
            for i in range(1, 3):  # Two questions
                prompt_text = f"Question{i}: difficulty Level:{difficulties[i-1]}"
                response = self._get_response(prompt_text, warn)
                
                if not response:
                    return None
                
                message = self._process_json_response(
                    response,
                    ["question"],
                    f"TwoPartAnalysisQuestion generate_question_text {i}"
                )
                
                if message and message.get("question"):
                    questions.append(message["question"])
                else:
                    return None
            
            return questions
        
        result = self._retry_generate(_generate)
        return result if result else []
    
    def generate_question_title(self) -> Optional[str]:
        """Generate TPA question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response("QuestionTitle", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "TwoPartAnalysisQuestion generate_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_solution(self) -> List[str]:
        """Generate TPA question solutions."""
        def _generate(warn: bool = False) -> Optional[List[str]]:
            solutions = []
            for i in range(1, 3):  # Two solutions
                prompt_text = f"QuestionSolution {i}"
                response = self._get_response(prompt_text, warn)
                
                if not response:
                    return None
                
                message = self._process_json_response(
                    response,
                    ["solution"],
                    f"TwoPartAnalysisQuestion generate_question_solution {i}"
                )
                
                if message and message.get("solution"):
                    solutions.append(message["solution"])
                else:
                    return None
            
            return solutions
        
        result = self._retry_generate(_generate)
        return result if result else []
    
    def generate_question_options(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate TPA question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response("QuestionOptions", warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"],
                "TwoPartAnalysisQuestion generate_question_options"
            )
            
            if message and message.get("options") and message.get("answer"):
                return message["options"], message["answer"]
            return None
        
        result = self._retry_generate(_generate)
        if result is None:
            return None, None
        return result


class MultiSourceReasoningQuestion(SpecializedQuestion):
    """Unified multi-source reasoning question component (GMAT only)."""
    
    def __init__(self, *args, **kwargs):
        """Initialize MSR question component."""
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.MULTI_SOURCE_REASONING
        self.temp_prompt = None
    
    def generate_source_info(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate source information for MSR questions."""
        self.temp_prompt = prompt
        
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(self.temp_prompt, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["sources", "source", "content"],
                "MultiSourceReasoningQuestion generate_source_info"
            )
            
            return message
        
        return self._retry_generate(_generate)
    
    def generate_main_question_title(self) -> Optional[str]:
        """Generate main title for MSR question set."""
        def _generate(warn: bool = False) -> Optional[str]:
            prompt_text = "MainQuestionTitle (based on the given question data what would be a unique question title of complete Multi Source Reasoning question)"
            response = self._get_response(prompt_text, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "MultiSourceReasoningQuestion generate_main_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_text(self, prompt: str) -> Optional[str]:
        """Generate MSR question text."""
        self.temp_prompt = prompt
        
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(self.temp_prompt, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["question"],
                "MultiSourceReasoningQuestion generate_question_text"
            )
            
            if message:
                return message.get("question")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_title(self, prompt: str) -> Optional[str]:
        """Generate MSR question title."""
        self.temp_prompt = prompt
        
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(self.temp_prompt, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["title"],
                "MultiSourceReasoningQuestion generate_question_title"
            )
            
            if message:
                return message.get("title")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_solution(self, prompt: str) -> Optional[str]:
        """Generate MSR question solution."""
        self.temp_prompt = prompt
        
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(self.temp_prompt, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["solution"],
                "MultiSourceReasoningQuestion generate_question_solution"
            )
            
            if message:
                return message.get("solution")
            return None
        
        return self._retry_generate(_generate)
    
    def generate_question_options(self, prompt: str, question_style: str) -> Union[Tuple[Any, Any], Any]:
        """Generate MSR question options based on question style."""
        self.temp_prompt = [prompt, question_style]
        
        def _generate(warn: bool = False) -> Optional[Union[Tuple[Any, Any], Any]]:
            response = self._get_response(prompt, warn)
            
            if not response:
                return None
            
            message = self._process_json_response(
                response,
                ["options", "answer"] if question_style == "MCQ (5 options MCQ)" else ["options"],
                "MultiSourceReasoningQuestion generate_question_options"
            )
            
            if message:
                if question_style == "MCQ (5 options MCQ)":
                    if message.get("options") and message.get("answer"):
                        return message["options"], message["answer"]
                else:
                    return message.get("options")
            return None
        
        if question_style == "MCQ (5 options MCQ)":
            result = self._retry_generate(_generate)
            if result is None:
                return None, None
            return result
        else:
            return self._retry_generate(_generate)


# Factory function for creating question components
def create_question_component(
    question_type: QuestionType,
    llm: genai.Client,
    system_instructions: str,
    global_state: Dict[str, Any],
    lock: Any,
    prompt: str,
    exam_type: ExamType = ExamType.GMAT
) -> BaseQuestionComponent:
    """
    Factory function to create appropriate question component.
    
    Args:
        question_type: Type of question to create
        llm: Google Generative AI client
        system_instructions: AI system instruction text
        global_state: Shared state for rate limiting
        lock: Thread lock for rate limiting
        prompt: Question generation prompt
        exam_type: Target exam type
        
    Returns:
        Appropriate question component instance
        
    Raises:
        QuestionGenerationException: If question type is not supported
    """
    component_map = {
        QuestionType.PROBLEM_SOLVING: SimpleQuestion,
        QuestionType.MULTIPLE_CHOICE_SINGLE: SimpleQuestion,
        QuestionType.MULTIPLE_CHOICE_MULTIPLE: SimpleQuestion,
        QuestionType.NUMERIC_ENTRY: SimpleQuestion,
        QuestionType.DATA_SUFFICIENCY: DataSufficiencyQuestion,
        QuestionType.READING_COMPREHENSION: ParentChildQuestion,
        QuestionType.CRITICAL_REASONING: SimpleQuestion,
        QuestionType.TEXT_COMPLETION: SimpleQuestion,
        QuestionType.SENTENCE_EQUIVALENCE: SimpleQuestion,
        QuestionType.SENTENCE_CORRECTION: SimpleQuestion,
    }
    
    # IR questions (GMAT only)
    if exam_type == ExamType.GMAT:
        component_map.update({
            QuestionType.GRAPHIC_INTERPRETATION: GraphicInterpretationQuestion,
            QuestionType.TABLE_ANALYSIS: TableAnalysisQuestion,
            QuestionType.TWO_PART_ANALYSIS: TwoPartAnalysisQuestion,
            QuestionType.MULTI_SOURCE_REASONING: MultiSourceReasoningQuestion,
        })
    
    component_class = component_map.get(question_type)
    if not component_class:
        raise QuestionGenerationException(
            f"Unsupported question type: {question_type} for exam type: {exam_type}"
        )
    
    return component_class(
        llm=llm,
        system_instructions=system_instructions,
        global_state=global_state,
        lock=lock,
        prompt=prompt,
        exam_type=exam_type,
        question_type=question_type
    )