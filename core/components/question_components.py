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
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union, Literal
from google import genai
from datetime import datetime
from google.genai import types

# Import core utilities created in CHUNK 1
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.difficulty_levels import DifficultyLevel
from core.utilities.json_utils import refine_response
from core.utilities.validation_utils import validate_prompt


class QuestionGenerationException(Exception):
    """Raised when question generation fails."""
    pass


# Global constants
WARNING_MESSAGE = "\nCRITICAL ERROR: Your response MUST be valid JSON only. EXAMPLE: {\"solution\": \"text here\"}. No text before/after JSON. No explanations. No markdown. Just pure JSON that can be parsed by json.loads(). Use (`) instead of single quotes inside strings."
MAX_RETRIES = 3
RATE_LIMIT_REQUESTS_PER_MINUTE = 9  # Use 9 instead of 10 for safety margin
RATE_LIMIT_WINDOW_SECONDS = 60

def _is_text_completion_prompt(prompt: str) -> bool:
    """Check if a prompt is for Text Completion questions."""
    prompt_lower = prompt.lower()
    return any(tc_type in prompt_lower for tc_type in ['<tc-1>', '<tc-2>', '<tc-3>', 'tc-1', 'tc-2', 'tc-3'])

def _is_reading_comprehension_prompt(prompt: str) -> bool:
    """Check if a prompt is for Reading Comprehension questions."""
    prompt_lower = prompt.lower()
    return '<rc-' in prompt_lower

def _log_reading_comprehension_data(prompt: str, response: str, mode: str = "unknown"):
    """Log Reading Comprehension instruction prompt and AI response for debugging."""
    try:
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "instruction_prompt": prompt,
            "ai_response": response,
            "rc_type_detected": None
        }
        
        # Detect RC type
        prompt_lower = prompt.lower()
        if '<rc-' in prompt_lower:
            if 'rc-s' in prompt_lower:
                log_entry["rc_type_detected"] = "RC-S"
            elif 'rc-m' in prompt_lower:
                log_entry["rc_type_detected"] = "RC-M"
            elif 'rc-l' in prompt_lower:
                log_entry["rc_type_detected"] = "RC-L"
            else:
                log_entry["rc_type_detected"] = "RC"
        elif 'reading comprehension' in prompt_lower:
            log_entry["rc_type_detected"] = "RC"
        
        # Store original prompt for reference
        if "Prompt: " in prompt:
            original_prompt = prompt.split("Prompt: ")[1].split("\n")[0]
            log_entry["original_prompt"] = original_prompt
        
        # Ensure testing-rc.json exists
        log_file = "testing-rc.json"
        
        # Load existing data or create new
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"reading_comprehension_logs": []}
        
        # Add new entry
        data["reading_comprehension_logs"].append(log_entry)
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error logging Reading Comprehension data: {e}")


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


def extract_dichotomous_type_from_prompt(prompt: str) -> Optional[List[str]]:
    """Extract dichotomous type from prompt.

    Args:
        prompt: The prompt string containing dichotomous type info

    Returns:
        List of dichotomous options or None if not found

    Examples:
        "ChildQuestion: 1 <Data Interpretation> - <Dichotomous Choice(Yes/No)> - <3>" -> ["Yes", "No"]
        "ChildQuestion: 2 <Critical Reasoning> - <Dichotomous Choice(Would Help/Would Not Help)> - <4>" -> ["Would Help", "Would Not Help"]
    """
    # Look for dichotomous choice pattern
    dichotomous_pattern = r'<Dichotomous Choice\(([^)]+)\)>'
    match = re.search(dichotomous_pattern, prompt)

    if match:
        choices_str = match.group(1)
        # Split by / and clean up
        choices = [choice.strip() for choice in choices_str.split('/')]
        return choices

    return None


def replace_dichotomous_tokens(template_text: str, dichotomous_options: List[str]) -> str:
    """Replace {type} tokens in template with random dichotomous options.

    Args:
        template_text: Template text containing {type} tokens
        dichotomous_options: List of dichotomous options (e.g., ["Yes", "No"])

    Returns:
        Template text with {type} tokens replaced
    """
    if not dichotomous_options:
        return template_text

    # Replace each {type} token with a random choice
    def replace_token(match):
        return random.choice(dichotomous_options)

    # Replace all {type} tokens
    result = re.sub(r'\{type\}', replace_token, template_text)

    return result


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
            raise QuestionGenerationException(
                f"Invalid prompt format: {prompt}")

        # Initialize exam-specific adapter
        self._adapter = self._initialize_adapter()

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
            config.thinking_config = types.ThinkingConfig(
                include_thoughts=True)

        return self.llm.chats.create(
            model=os.getenv("MODEL", "gemini-2.5-flash-preview-05-20"),
            config=config
        )

    def _initialize_adapter(self):
        """Initialize the appropriate adapter for the exam type."""
        if self.exam_type == ExamType.GMAT:
            from core.components.adapters.gmat_adapter import GMATAdapter
            return GMATAdapter()
        else:  # GRE
            from core.components.adapters.gre_adapter import GREAdapter
            return GREAdapter()

    def _load_customizations(self) -> Optional[Dict[str, Any]]:
        """Load exam-specific customizations for template processing."""
        try:
            from core.instructions.instruction_loader import InstructionLoader
            loader = InstructionLoader()
            return loader.load_customizations(self.exam_type, self.question_type)
        except Exception as e:
            print(f"Warning: Could not load customizations: {e}")
            return {}

    def _get_component_instruction(self, component_name: Literal[
        'QuestionMetadata',
        'QuestionSolution',
        'QuestionOptions',
        'QuestionText',
        'QuestionTitle',
        'QuestionAnswer',
        'QuestionPassage',
        'ParentQuestion',
        'ParentTitle',
        'ChildQuestion',
        'ChildTitle',
        'ChildSolution',
    ], source_type: str = None) -> str:
        """
        Get template-based instruction for a specific component using new template classes.

        Args:
            component_name: Name of the component
            options: ['QuestionMetadata', 'QuestionSolution', 'QuestionOptions', 'QuestionText', 'QuestionTitle', 'QuestionAnswer', 'QuestionPassage', 'ParentQuestion', 'ParentTitle', 'ChildQuestion','ChildTitle', 'ChildSolution']
        Returns:
            Template-based instruction text
        """
        try:
            # Load customizations for template processing
            customizations = self._load_customizations()

            # Use adapter to get appropriate template based on component type
            if component_name == "QuestionSolution":
                instruction = self._adapter.get_solution_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "QuestionOptions":
                instruction = self._adapter.get_options_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "QuestionText":
                instruction = self._adapter.get_text_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "QuestionTitle":
                instruction = self._adapter.get_title_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "QuestionAnswer":
                instruction = self._adapter.get_answer_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "QuestionPassage" or component_name == "QuestionMetadata":
                # Both QuestionPassage and multiSource map to metadata templates
                instruction = self._adapter.get_metadata_template(
                    self.question_type, self.prompt, customizations, source_type
                )
            elif component_name == "ParentQuestion":
                # Parent question content (passages for RC)
                instruction = self._adapter.get_text_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "ParentTitle":
                # Parent title
                instruction = self._adapter.get_title_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "ChildQuestion":
                # Child question text
                instruction = self._adapter.get_text_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "ChildTitle":
                # Child question title
                instruction = self._adapter.get_title_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "ChildSolution":
                # Child question solution
                instruction = self._adapter.get_solution_template(
                    self.question_type, self.prompt, customizations
                )
            elif component_name == "ChildOptions":
                # Child question options
                instruction = self._adapter.get_options_template(
                    self.question_type, self.prompt, customizations
                )
            else:
                # Fallback for any unmapped component types
                instruction = self._adapter.get_metadata_template(
                    self.question_type, self.prompt, customizations
                )

            # Handle dichotomous token replacement for QuestionOptions
            if component_name == "QuestionOptions" and instruction:
                dichotomous_options = extract_dichotomous_type_from_prompt(
                    self.prompt)
                if dichotomous_options:
                    instruction = replace_dichotomous_tokens(
                        instruction, dichotomous_options)

            return instruction

        except Exception as e:
            print(
                f"Warning: Could not load template instruction for {component_name}: {e}")
            # Fallback to simple component name
            return component_name

    def _get_response(self, prompt: str, warn: bool = False) -> Optional[str]:
        """
        Get response from AI with rate limiting and error handling.

        Args:
            prompt: The prompt to send to AI
            warn: Whether to append warning message

        Returns:
            AI response text or None if failed
        """

        # Store the original prompt for debugging
        self._last_prompt_sent = prompt

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
            if response and response.text:
                # Log Reading Comprehension questions for debugging
                if _is_reading_comprehension_prompt(prompt):
                    _log_reading_comprehension_data(prompt, response.text, "AI_Response")
                return response.text
            else:
                print(f"Empty response from AI - response: {response}")
                return None
        except Exception as e:
            error_str = str(e).lower()

            # Handle 429 errors with simple output
            if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
                # print(f"API error code:- 429\t\t {time.strftime('%H:%M:%S')}")
                # Extract retry delay if available
                if "retrydelay" in error_str or "retry" in error_str:
                    try:
                        # Try to extract retry delay from error message
                        import re
                        delay_match = re.search(r'(\d+)s', error_str)
                        if delay_match:
                            delay = int(delay_match.group(1))
                            # print(f"Waiting {delay} seconds for API rate limit reset...")
                            time.sleep(delay + 1)  # Add 1 second buffer
                        else:
                            # print("Waiting 60 seconds for API rate limit reset...")
                            time.sleep(60)
                    except:
                        # print("Waiting 60 seconds for API rate limit reset...")
                        time.sleep(60)
            else:
                # For other errors, show minimal info
                print(f"Generation error: {type(e).__name__} - {str(e)}")

            # Reset rate limiting state on any error
            with self.lock:
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
        import inspect

        # Get the parent function name from call stack
        parent_function = "unknown"
        try:
            # Get the calling frame (parent function that called _retry_generate)
            frame = inspect.currentframe().f_back
            parent_function = frame.f_code.co_name
        except:
            parent_function = "unknown"

        last_error = None
        failure_reason = None
        last_response = None

        # Global counter for call priority across all components
        if not hasattr(self, '_call_priority_counter'):
            self._call_priority_counter = 1
        else:
            self._call_priority_counter += 1

        for attempt in range(self.max_retries):
            try:
                # Add warn parameter for retries
                result = func(*args, warn=(attempt > 0), **kwargs)

                if result is not None:  # Accept any non-None result
                    return result
                failure_reason = "No result returned (None)"
                if (attempt > 0):  # Only print retry messages for attempts 2 and 3
                    print(
                        f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}\t\tParent Function: {parent_function}\t\tReason: {failure_reason}")

            except Exception as e:
                last_error = str(e)
                failure_reason = f"Exception: {last_error}"
                if (attempt > 0):  # Only print retry messages for attempts 2 and 3
                    print(
                        f"Retrying {func.__name__} - attempt {attempt + 1}/{self.max_retries}\t\tParent Function: {parent_function}\t\tReason: {failure_reason}")

                # Exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

        # All attempts failed

        if last_error:
            print(
                f"All attempts failed for {parent_function}. Last error: {last_error}")
        else:
            print(
                f"All attempts failed for {parent_function}. Reason: {failure_reason}")
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
            if not response or not response.strip():
                print(f"Empty response received for {context}")
                return None

            refined = refine_response(response)
            if not refined:
                print(f"Refine response returned empty for {context}")
                return None

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
        # Use the question_type passed from parent, don't override it
        if self.question_type is None:
            self.question_type = QuestionType.PROBLEM_SOLVING  # Default only if not set

    def generate_question_passage(self, instruction_prompt: str) -> str:
        """
        Generate question passage/argument for Critical Reasoning questions.

        Returns:
            Generated passage text
        """
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["passage"],
                "SimpleQuestion generate_question_passage"
            )

            if message and message.get("passage"):
                return message["passage"]
            return None

        result = self._retry_generate(_generate)
        return result if result else "Error generating question passage"

    def generate_question_text(self, instruction_prompt: str) -> str:
        """
        Generate question text.

        Args:
            instruction_prompt: Full instruction prompt including component template

        Returns:
            Generated question text
        """
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                print(
                    f"No response received for QuestionText prompt: {instruction_prompt}")
                return None

            message = self._process_json_response(
                response,
                ["question"],
                "SimpleQuestion generate_question_text"
            )

            if message and message.get("question"):
                return message["question"]
            else:
                print(
                    f"No question field found in response for prompt: {instruction_prompt}")
                if message:
                    print(f"Available fields: {list(message.keys())}")
                return None

        result = self._retry_generate(_generate)
        return result if result else "Error generating question text"

    def generate_question_title(self, instruction_prompt: str) -> str:
        """Generate question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_solution(self, instruction_prompt: str, instruction_prompt2: str = None, is_numeric_entry: bool = False) -> Union[str, Tuple[str, float]]:
        """
        Generate question solution.

        Args:
            instruction_prompt: for question component
            instruction_prompt2: for answer component
            is_numeric_entry: Whether this is a numeric entry question (GRE only)

        Returns:
            Solution string for MCQ, or (solution, answer) tuple for numeric entry
        """
        if is_numeric_entry:
            # For numeric entry, we need both solution and answer
            # Solution is plain text, answer is JSON
            solution = self._generate_solution_plain_text(instruction_prompt)
            answer = self._generate_answer_numeric(instruction_prompt2)
            return solution, answer
        else:
            # For regular questions, just solution as plain text
            return self._generate_solution_plain_text(instruction_prompt)

    def _generate_solution_plain_text(self, instruction_prompt: str) -> str:
        """Generate solution as plain text for all the questions regardless of type of question!."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                print("No response received for QuestionSolution")
                return None

            # For solution mode, AI returns plain text directly
            stripped_response = response.strip()
            if not stripped_response:
                print("Empty response after stripping for QuestionSolution")
                return None
            return stripped_response

        result = self._retry_generate(_generate)
        return result if result else ""

    def _generate_answer_numeric(self, instruction_prompt: str) -> float:
        """Generate numeric answer for numeric entry questions."""
        def _generate(warn: bool = False) -> Optional[float]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["answer"],
                "SimpleQuestion generate_answer_numeric"
            )

            if message and message.get("answer") is not None:
                try:
                    return float(message["answer"])
                except (ValueError, TypeError):
                    print(
                        f"Warning: Could not convert answer to float: {message['answer']}")
                    return 0.0
            return None

        result = self._retry_generate(_generate)
        return result if result is not None else 0.0

    def generate_question_answer(self, instruction_prompt: str) -> str:
        """Generate question answer letter only."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)
            if not response:
                print("No response received for QuestionAnswer")
                return None
            # Parse JSON response to extract answer
            message = self._process_json_response(
                response,
                ["answer"],
                "SimpleQuestion generate_question_answer"
            )
            if message and message.get("answer"):
                return str(message["answer"]).strip()
            return None
        result = self._retry_generate(_generate)
        return result if result else ""

    def generate_question_options(self, instruction_prompt: str) -> Tuple[Dict[str, str], str]:
        """
        Generate question options and correct answer.

        Returns:
            Tuple of (options_dict, correct_answer_key)

        The options_dict will be in format: {"A": "option1", "B": "option2", ...}
        The correct_answer_key will be the letter key: "A", "B", etc.
        """
        def _generate(warn: bool = False) -> Optional[Tuple[Dict[str, str], str]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["options", "answer"],
                "SimpleQuestion generate_question_options"
            )

            if message and message.get("options") and message.get("answer"):
                options = message["options"]
                answer = message["answer"]

                # Validate that options is a dictionary
                if not isinstance(options, dict):
                    print(
                        f"ERROR: Options should be a dictionary but got {type(options)}: {options}")
                    return None

                # Validate that all option keys are single letters
                for key in options.keys():
                    if not isinstance(key, str) or len(key) != 1 or not key.isalpha():
                        print(
                            f"ERROR: Option key should be single letter but got: {key}")
                        return None

                # Validate that answer is a valid key or list of valid keys
                if isinstance(answer, str):
                    if answer not in options:
                        print(
                            f"ERROR: Answer key '{answer}' not found in options: {list(options.keys())}")
                        return None
                elif isinstance(answer, list):
                    for ans_key in answer:
                        if ans_key not in options:
                            print(
                                f"ERROR: Answer key '{ans_key}' not found in options: {list(options.keys())}")
                            return None
                else:
                    print(
                        f"ERROR: Answer should be string or list but got {type(answer)}: {answer}")
                    return None

                return options, answer
            return None

        result = self._retry_generate(_generate)
        return result if result else ({}, "")


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

    def generate_question_graph(self, instruction_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate question graph/table if needed."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["graph/table", "graph"],
                "DataSufficiencyQuestion generate_question_graph"
            )

            if message:
                # Return the first non-None value from the response
                for key in ["graph/table", "graph", "table"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                # If all values are None, return the entire message as fallback
                return message
            return None

        return self._retry_generate(_generate)

    def generate_question_text(self, instruction_prompt: str) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """
        Generate question text components.

        Returns:
            Tuple of (passage, statements_list, question)
        """
        def _generate(warn: bool = False) -> Optional[Tuple[str, List[str], str]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # Accept both GMAT and GRE key patterns for flexibility
            expected_keys = ["passage", "statements", "question"]

            message = self._process_json_response(
                response,
                expected_keys,
                "DataSufficiencyQuestion generate_question_text"
            )

            if not message:
                return None

            # Extract components - use consistent format
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

    def generate_question_title(self, instruction_prompt: str) -> Optional[str]:
        """Generate question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_solution(self, instruction_prompt: str) -> str:
        """
        Generate question solution only (without answer).

        Returns:
            Solution text as plain text
        """
        # Generate solution only - answer will be generated with options
        return self._generate_solution_only(instruction_prompt)

    def generate_question_options_with_answer(self, instruction_prompt: str) -> Tuple[Dict[str, str], str]:
        """
        Generate question options and answer together.

        Returns:
            Tuple of (options_dict, correct_answer_key)
        """
        # For Data Sufficiency, we use standard options but still need to determine the answer
        # Standard data sufficiency options
        standard_options = {
            "A": "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.",
            "B": "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient.",
            "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement ALONE is sufficient.",
            "D": "EACH statement ALONE is sufficient.",
            "E": "Statements (1) and (2) TOGETHER are NOT sufficient."
        }

        # Generate the answer key using the AI
        answer = self._generate_answer_only(instruction_prompt)

        return standard_options, answer

    def _generate_solution_only(self, instruction_prompt: str) -> str:
        """Generate only the solution text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # receiving as Plain text for all the questions
            return response.strip() if response else None

        result = self._retry_generate(_generate)
        if result is None:
            print("Warning: Solution generation failed, using fallback")
            return "Solution could not be generated due to technical issues. Please refer to standard Data Sufficiency strategies."
        return result

    def _generate_answer_only(self, instruction_prompt: str) -> str:
        """Generate only the answer letter."""
        def _generate(warn: bool = False) -> Optional[str]:
            # Use standardized naming across all exams
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # Try to process as JSON first
            message = self._process_json_response(
                response,
                ["answer"],
                "DataSufficiencyQuestion generate_answer_only"
            )

            if message and message.get("answer"):
                answer = str(message["answer"]).strip()
                return answer

            # If JSON parsing failed, the AI might have returned plain text
            # In this case, we should return the response as-is since it's supposed to be JSON
            print(f"Warning: Answer generation returned non-JSON format, using fallback")
            return None

        result = self._retry_generate(_generate)
        if result is None:
            print("Warning: Answer generation failed, using fallback")
            return "A"  # Use reasonable fallback - could be made configurable
        return result

    def generate_question_options(self, instruction_prompt: str) -> Tuple[List[str], str]:
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
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_passage(self, instruction_prompt: str) -> str:
        """
        Generate question passage for Reading Comprehension questions.

        Returns:
            Generated passage text
        """
        def _generate(warn: bool = False) -> str:
            prompt_text = f"mode:- ParentQuestion (Active) generate passage;\n {instruction_prompt}"
            response = self._get_response(prompt_text, warn)

            if not response:
                return ""

            parsed_data = self._process_json_response(
                response, 
                expected_keys=["passage"], 
                context="generate_question_passage"
            )
            
            if parsed_data and isinstance(parsed_data, dict):
                passage = parsed_data.get("passage", "")
                return passage.strip() if passage else ""
            else:
                return response.strip()

        # Generate the passage
        try:
            result = _generate()
            if not result:
                # Retry with warning
                result = _generate(warn=True)
            
            return result if result else ""
        except Exception as e:
            self.logger.log_generation_error(e, {
                "operation": "ParentChildQuestion generate_question_passage",
                "instruction_prompt": instruction_prompt[:100]
            })
            return ""

    def generate_question_metadata(self, instruction_prompt: str, i=0, total=0) -> Optional[Dict[str, Any]]:
        """Generate shared graph/table for child questions or passage for reading comprehension."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            # Determine command format based on exam type and question content
            if any(term in instruction_prompt.lower() for term in ["rc-", "reading_comprehension", "questionpassage"]):
                prompt_text = f"mode:- ParentQuestion (Active) generate passage paragraph {i} of {total};\n {instruction_prompt}"
            else:
                prompt_text = f"mode:- questionGraph input:- {instruction_prompt}"

            response = self._get_response(prompt_text, warn)

            if not response:
                return None

            # Accept multiple possible key formats for flexibility
            expected_keys = ["passage", "graph/table"]

            message = self._process_json_response(
                response,
                expected_keys,
                "ParentChildQuestion generate_question_metadata"
            )

            if message:
                # Check what type of content we received and return accordingly
                if "passage" in message:
                    # This is Reading Comprehension passage data
                    return message
                elif "graph/table" in message or "graph" in message or "table" in message:
                    # This is quantitative graph/table data
                    # Return the first non-None value from the response
                    for key in ["graph/table", "graph", "table"]:
                        value = message.get(key)
                        if value is not None:
                            return value
                    # If all values are None, return the entire message
                    return message
                else:
                    # Fallback - return the whole message
                    return message
            return None

        return self._retry_generate(_generate)

    def generate_question_graph(self, instruction_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate question graph/table if needed."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["graph/table", "graph"],
                "ParentChildQuestion generate_question_graph"
            )

            if message:
                for key in ["graph/table", "graph", "table"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                return message
            return None

        return self._retry_generate(_generate)

    def generate_question_table(self, instruction_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate question table if needed."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["tables", "content", "table"],
                "ParentChildQuestion generate_question_table"
            )

            if message:
                for key in ["tables", "content", "table"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                return message
            return None

        return self._retry_generate(_generate)

    def generate_parent_title(self, instruction_prompt: str = "") -> Optional[str]:
        """Generate title for parent question set."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)
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

    def generate_child_question_title(self, index: int, instruction_prompt: str = "") -> Optional[str]:
        """Generate title for specific child question."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(
                f"mode:- ChildQuestionTitle for question {index}:\n{instruction_prompt}", warn)

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

    def generate_child_question(self, index: int, instruction_prompt: str = "") -> Optional[str]:
        """Generate specific child question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(
                f"mode:- childQuestionText for question {index}:\n{instruction_prompt}", warn)

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

    def generate_child_options(self, index: int, instruction_prompt: str = "") -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate options and answer for specific child question."""
        def _generate(warn: bool = False) -> Optional[Tuple[List[str], str]]:
            response = self._get_response(
                f"mode:- childOptions for question {index}:\n{instruction_prompt}", warn)

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

    def generate_child_solution(self, index: int, instruction_prompt: str = "") -> Optional[str]:
        """Generate solution for specific child question."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(
                f"mode:- childSolution for question {index}:\n{instruction_prompt}", warn)

            if not response:
                return None

            # For solution mode, AI returns plain text directly
            return response.strip() if response else None

        return self._retry_generate(_generate)

    def generate_child_answer(self, index: int, instruction_prompt: str) -> Optional[str]:
        """Generate answer for specific child question."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)
            if not response:
                return None
            # Parse JSON response to extract answer
            message = self._process_json_response(
                response,
                ["answer"],
                f"ParentChildQuestion generate_child_answer {index}"
            )
            if message:
                return message.get("answer")
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

    def generate_question_graph(self, instruction_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate graph/chart for GI question."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["graph"],
                "GraphicInterpretationQuestion generate_question_graph"
            )

            return message

        return self._retry_generate(_generate)

    def generate_question_text(self, instruction_prompt: str) -> Optional[str]:
        """Generate GI question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_title(self, instruction_prompt: str) -> Optional[str]:
        """Generate GI question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_solution(self, instruction_prompt: str) -> Optional[str]:
        """Generate GI question solution."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # For solution mode, AI returns plain text directly
            return response.strip() if response else None

        return self._retry_generate(_generate)

    def generate_question_options(self, instruction_prompt) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate GI question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_table(self, instruction_prompt: str, num_rows: int, num_cols: int) -> Optional[Dict[str, Any]]:
        """Generate table for TA question."""
        self.temp_data = [num_rows, num_cols]

        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            prompt_text = f"mode:- QuestionTable, no_rows: {num_rows}, no_cols: {num_cols};\n {instruction_prompt}"
            response = self._get_response(prompt_text, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["tables", "content", "table"],
                "TableAnalysisQuestion generate_question_table"
            )

            if message:
                # Return the first non-None value from the response
                for key in ["tables", "content", "table"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                # If all values are None, return the entire message as fallback
                return message
            return None

        return self._retry_generate(_generate)

    def generate_question_text(self, instruction_prompt: str) -> Optional[str]:
        """Generate TA question text."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["question", "text", "content", "title"],
                "TableAnalysisQuestion generate_question_text"
            )

            if message:
                # Return the first non-None value from the response
                for key in ["question", "text", "content", "title"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                # If all values are None, return the entire message as fallback
                return message
            return None

        return self._retry_generate(_generate)

    def generate_question_title(self, instruction_prompt: str) -> Optional[str]:
        """Generate TA question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_solution(self, instruction_prompt: str) -> Optional[str]:
        """Generate TA question solution."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # For solution mode, AI returns plain text directly
            return response.strip() if response else None

        return self._retry_generate(_generate)

    def generate_question_answer(self, instruction_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate TA question answer."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["answer"],
                "TableAnalysisQuestion generate_question_answer"
            )

            if message:
                return message.get("answer")
            return None

        return self._retry_generate(_generate)

    def generate_question_options(self, instruction_prompt: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate TA question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_parent_question_content(self, instruction_prompt) -> Optional[Dict[str, Any]]:
        """Generate shared content for TPA questions."""
        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["content", "question", "graph", "data"],
                "TwoPartAnalysisQuestion generate_parent_question_content"
            )

            if message:
                # Return the first non-None value from the response
                for key in ["content", "question", "graph", "data"]:
                    value = message.get(key)
                    if value is not None:
                        return value
                # If all values are None, return the entire message as fallback
                return message
            return None

        return self._retry_generate(_generate)

    def generate_question_text(self, instruction_prompt: str, difficulties: List[int]) -> List[str]:
        """Generate TPA question texts with different difficulties."""
        def _generate(warn: bool = False) -> Optional[List[str]]:
            questions = []
            for i in range(1, 3):  # Two questions
                prompt_text = f"Question{i}: difficulty Level:{difficulties[i-1]}\n {instruction_prompt}"
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

    def generate_question_title(self, instruction_prompt) -> Optional[str]:
        """Generate TPA question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(
                f"mode:- QuestionTitle\n{instruction_prompt}", warn)

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

    def generate_question_solution(self, instruction_prompt: str) -> List[str]:
        """Generate TPA question solutions."""
        def _generate(warn: bool = False) -> Optional[List[str]]:
            solutions = []
            for i in range(1, 3):  # Two solutions
                prompt_text = f"QuestionSolution {i}:- \n {instruction_prompt}"
                response = self._get_response(prompt_text, warn)

                if not response:
                    return None

                # For solution mode, AI returns plain text directly
                solution_text = response.strip()
                if solution_text:
                    solutions.append(solution_text)
                else:
                    return None

            return solutions

        result = self._retry_generate(_generate)
        return result if result else []

    def generate_question_answers(self, instruction_prompt: str) -> List[str]:
        """Generate TPA question answers."""
        def _generate(warn: bool = False) -> Optional[List[str]]:
            answers = []
            for i in range(1, 3):  # Two answers
                prompt_text = f"QuestionAnswer {i}:\n{instruction_prompt}"
                response = self._get_response(prompt_text, warn)

                if not response:
                    return None

                message = self._process_json_response(
                    response,
                    ["answer"],
                    f"TwoPartAnalysisQuestion generate_question_answers {i}"
                )

                if message and message.get("answer"):
                    answers.append(str(message["answer"]))
                else:
                    return None

            return answers

        result = self._retry_generate(_generate)
        return result if result else []

    def generate_question_options(self, instruction_prompt: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Generate TPA question options and answers."""
        def _generate(warn: bool = False) -> Optional[Tuple[Any, Any]]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_source_info(self, instruction_prompt: List[str], source_index: int = 1) -> Optional[Dict[str, Any]]:
        """Generate source information for MSR questions with proper template formatting."""
        # Change the prompt format to match metadata.json structure
        # From: "Generate SourceInfo_1 having Line Chart of question: MSR - <Business> - <Data Interpretation> - <difficulty_level: 2>"

        def _generate(warn: bool = False) -> Optional[Dict[str, Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["source_info", "content", "sources", "source"],
                "MultiSourceReasoningQuestion generate_source_info"
            )

            return message

        return self._retry_generate(_generate)

    def generate_main_question_title(self, instruction_prompt: str) -> Optional[str]:
        """Generate main title for MSR question set."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_text(self, instruction_prompt: str) -> Optional[str]:
        """Generate MSR question text."""

        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_title(self, instruction_prompt: str) -> Optional[str]:
        """Generate MSR question title."""
        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

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

    def generate_question_solution(self, instruction_prompt: str) -> Optional[str]:
        """Generate MSR question solution."""

        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            # For solution mode, AI returns plain text directly
            return response.strip() if response else None

        return self._retry_generate(_generate)

    def generate_question_answer(self, instruction_prompt: str) -> Optional[str]:
        """Generate MSR question answer."""

        def _generate(warn: bool = False) -> Optional[str]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["answer"],
                "MultiSourceReasoningQuestion generate_question_answer"
            )

            if message:
                return message.get("answer")
            return None

        return self._retry_generate(_generate)

    def generate_question_options(self, instruction_prompt: str, question_style: str = "MCQ (5 options MCQ)") -> Union[Tuple[Any, Any], Any]:
        """Generate MSR question options based on question style."""

        def _generate(warn: bool = False) -> Optional[Union[Tuple[Any, Any], Any]]:
            response = self._get_response(instruction_prompt, warn)

            if not response:
                return None

            message = self._process_json_response(
                response,
                ["options", "answer"] if question_style == "MCQ (5 options MCQ)" else [
                    "options"],
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
