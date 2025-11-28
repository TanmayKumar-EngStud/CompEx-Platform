"""
Generic Gemini generator for qGen-new system.

This module provides a unified interface for generating question components
using Google's Gemini API with rate limiting and error handling.
"""

import os
import json
import time
import threading
import re
from typing import Dict, Any, Optional, Union, List, get_origin
from google import genai
from google.genai import types
from dotenv import load_dotenv

from io_utils import prettify, record

# Load environment variables from the root directory
# Get the project root directory (two levels up from qGen-new)
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)


def refine_response(response_text: str) -> str:
    """
    Refines JSON responses, handles wrapped json```{block}``` and properly 
    handles newlines inside values and keys.

    Args:
        response_text: Raw response text from API

    Returns:
        Cleaned and formatted JSON string
    """
    if not response_text or response_text.strip() == "":
        print("Warning: Empty response received")
        return '{"error": "Empty response received"}'

    def clean_json_string(text: str) -> Optional[str]:
        """Clean JSON string to fix common formatting issues."""
        # Remove any leading/trailing whitespace and non-JSON content
        text = text.strip()

        # Remove any markdown code block indicators
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```', '', text, flags=re.MULTILINE)

        # Fix backticks inside JSON strings - replace backticks with single quotes
        # This is done before JSON parsing to prevent parsing errors
        text = re.sub(r'`([^`]*)`', r"'\1'", text)

        # Remove standalone backticks that might break JSON
        text = text.replace('`', "'")

        # Fix common JSON formatting issues
        # Fix trailing commas before closing brackets/braces
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # Fix double quotes inside strings (escape them)
        # This is a simplified approach - real implementation would be more complex

        return text

    try:
        # First, try to clean the response
        cleaned_text = clean_json_string(response_text)

        # Test if it's valid JSON
        json.loads(cleaned_text)
        return cleaned_text

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")

        # Try additional cleaning steps
        try:
            # More aggressive cleaning
            text = response_text.strip()

            # Extract JSON from markdown blocks
            json_match = re.search(
                r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            elif '```' in text:
                # Remove all markdown formatting
                text = re.sub(r'```[a-zA-Z]*\n?', '', text)
                text = re.sub(r'```', '', text)

            # Fix common issues
            text = text.strip()
            # Remove trailing commas
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            # Replace backticks with single quotes
            text = text.replace('`', "'")

            # Test the cleaned version
            json.loads(text)
            return text

        except json.JSONDecodeError:
            # If all else fails, return an error response
            error_msg = f"Failed to parse JSON response: {str(e)}"
            print(f"Warning: {error_msg}")
            return f'{{"error": "{error_msg}"}}'

    except Exception as e:
        error_msg = f"Unexpected error in refine_response: {str(e)}"
        print(f"Warning: {error_msg}")
        return f'{{"error": "{error_msg}"}}'


class GeminiGenerator:
    """
    Generic Gemini generator that handles API calls for question component generation.

    This class provides a unified interface for making Gemini API calls with
    rate limiting, error handling, and JSON response parsing.
    """

    def __init__(self, api_key_index: int = 0, max_retries: int = 3, question_type: str = None):
        """
        Initialize the Gemini generator.

        Args:
            api_key_index: Index of the API key to use (default: 0)
            max_retries: Maximum number of retry attempts (default: 3)
            question_type: Type of question for loading appropriate system instructions
        """
        self.api_key_index = api_key_index
        self.max_retries = max_retries
        self.question_type = question_type
        self.lock = threading.Lock()
        self.request_counter = 0
        self._last_request_ts = 0.0
        self._rate_limit_hits = 0
        self.min_request_interval = float(
            os.getenv('GEMINI_MIN_INTERVAL', '0'))
        self.min_retry_wait = int(os.getenv('GEMINI_MIN_RETRY_WAIT', '5'))
        self.question_type_slug = re.sub(
            r'[^a-zA-Z0-9]+', '-',
            (self.question_type or 'unknown')).strip('-') or 'question'

        # Remove manual rate limiting - rely on API's resource exhaustion handling
        # Remove manual rate limiting - rely on API's resource exhaustion handling

        # Load system instructions based on question type
        self.system_instructions = self._load_system_instructions()
        record(self.system_instructions,
               fname=f'system_instruction_{self.question_type_slug}',
               addresses=('gemini', 'system_instructions'))

        # Initialize API client
        self._initialize_api_client()

    def _load_system_instructions(self) -> str:
        """
        Load system instructions based on question type using get_Component_Template.

        Returns:
            System instruction text for the question type
        """
        if not self.question_type:
            return "You are a helpful AI assistant that generates educational content in the requested format."

        try:
            # Import get_Component_Template and get_json from io_utils
            from io_utils import get_Question_Template, get_json

            # Load question type info to get the system instruction template
            qt_info = get_json('question_type_info')[0]

            if self.question_type not in qt_info:
                raise ValueError(
                    f"Question type {prettify(self.question_type, 'Red')} not found in question_type_info.json")

            question_config = qt_info[self.question_type]
            system_instruction_template = question_config.get(
                'system-instruction')

            if not system_instruction_template:
                raise ValueError(
                    f"No system-instruction defined for {prettify(self.question_type, 'Red')}")

            # Use get_Question_Template to load the system instruction
            # We'll create a new component type "SystemInstruction" for this
            system_instructions = get_Question_Template(
                question_component="SystemInstruction",
                filename=system_instruction_template,
                exam_type="GRE",  # Default, will be overridden by template conditionals
                Section_name="General",
                question_type=self.question_type,
                variable=None
            )
            return system_instructions

        except Exception as e:
            raise ValueError(
                f"❌ Error loading system instructions for {prettify(self.question_type, 'Red')}: {str(e)}")

    def _initialize_api_client(self):
        """Initialize the Gemini API client."""
        try:
            api_key = self._get_api_key(self.api_key_index)
            self.client = genai.Client(api_key=api_key)
            # print(
            #     f"✅ Gemini generator initialized with API key index {self.api_key_index}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Gemini API client: {str(e)}")

    def _get_api_key(self, index: int) -> str:
        """Get API key by index from environment variables."""
        key_name = f"API_{index}"
        api_key = os.getenv(key_name)

        if not api_key:
            raise ValueError(
                f"API key {key_name} not found in environment variables")

        return api_key

    def _create_chat_instance(self, system_instructions: str) -> Any:
        """Create a chat instance with system instructions."""
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instructions
            )

            model_name = os.getenv("MODEL2", "gemini-1.5-flash")
            return self.client.chats.create(
                model=model_name,
                config=config
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create chat instance: {str(e)}")

    def _parse_json_response(self, response_text: str, expected_output: Union[str, Dict[str, str]]) -> Union[str, Dict[str, Any]]:
        """
        Parse response based on expected output format using refine_response for JSON cleaning.

        Args:
            response_text: Raw response text from Gemini
            expected_output: Expected output format (str for plain text, dict for JSON keys)

        Returns:
            Either plain string or parsed JSON data containing the expected keys
        """
        try:
            # If expected output is a plain string, return the response directly
            if expected_output == "str":
                # Clean any markdown formatting but keep the content
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```') and cleaned_text.endswith('```'):
                    # Remove markdown code block formatting
                    lines = cleaned_text.split('\n')
                    if len(lines) > 2:
                        cleaned_text = '\n'.join(lines[1:-1])
                return cleaned_text

            # For JSON responses, use refine_response to clean and then parse
            refined_response = refine_response(response_text)

            # Check if refine_response returned an error
            if refined_response.startswith('{"error":'):
                raise ValueError(
                    f"refine_response returned error: {refined_response}")

            # Parse the refined JSON
            parsed_data = json.loads(refined_response)

            # Check if this is an error response from refine_response
            if isinstance(parsed_data, dict) and "error" in parsed_data and len(parsed_data) == 1:
                raise ValueError(
                    f"refine_response error: {parsed_data['error']}")

            # Validate expected output keys
            if get_origin(expected_output) is dict:
                for key, expected_type in expected_output.items():
                    if key not in parsed_data:
                        raise ValueError(
                            f"Missing expected key '{prettify(key, 'Magenta')}' in response")

                    # Basic type validation with more flexible handling
                    if expected_type == "str" and not isinstance(parsed_data[key], str):
                        raise ValueError(
                            f"Expected string for '{key}', got {type(parsed_data[key])}")
                    elif expected_type == "dict" and not isinstance(parsed_data[key], (dict, list)):
                        # Accept both dict and list for expected dict types (since both can be JSON serialized)
                        raise ValueError(
                            f"Expected dict or list for '{key}', got {type(parsed_data[key])}")
                    elif expected_type == "dict" and isinstance(parsed_data[key], list):
                        # Special handling for options that might come as list of dicts
                        if key == "options":
                            # Convert list of option dicts to single dict
                            options_dict = {}
                            for item in parsed_data[key]:
                                if isinstance(item, dict):
                                    options_dict.update(item)
                            parsed_data[key] = options_dict
                        # For other keys like 'graph', 'table', etc., keep the list as-is
                        # since it's valid JSON data
                    elif expected_type == "List[str]" and not isinstance(parsed_data[key], list):
                        raise ValueError(
                            f"Expected list for '{key}', got {type(parsed_data[key])}")
                    elif expected_type == "int" and not isinstance(parsed_data[key], (int, float)):
                        raise ValueError(
                            f"Expected number for '{key}', got {type(parsed_data[key])}")

            return parsed_data

        except json.JSONDecodeError as e:
            # If JSON parsing fails but we expected a string, return the cleaned text
            if expected_output == "str":
                return response_text.strip()
            raise ValueError(
                f"Invalid JSON response after refinement: {str(e)}\nRefined response: {refined_response}\nOriginal response: {response_text}")
        except Exception as e:
            raise ValueError(
                f"Error parsing response: {str(e)}\nResponse text: {response_text}")

    def generate_component(self,
                           instruction_statement: str,
                           expected_output: Union[str, Dict[str, str]],
                           context: Optional[Dict[str, Any]] = None) -> Union[str, Dict[str, Any]]:
        """
        Generate a question component using Gemini API.

        Args:
            instruction_statement: Complete instruction for the component generation
            expected_output: Expected output format (str or dict describing output keys and types)
            context: Optional context information for debugging/logging

        Returns:
            Generated component data as dictionary

        Raises:
            RuntimeError: If generation fails after all retries
        """
        context = context or {}

        # Validate required context information
        component_type = context.get('component_type')
        original_prompt = context.get('original_prompt')

        if not component_type:
            raise ValueError(
                f"Missing required {prettify('component_type', 'Red')} in context for component generation")

        if not original_prompt:
            raise ValueError(
                f"Missing required {prettify('original_prompt', 'Red')} in context for {prettify(component_type, 'Yellow')} generation")

        attempt = 0
        rpd_flag = 0 # Request Per Day flag: 0 = OK, 1 = Warning/Waiting
        
        while attempt < self.max_retries:
            try:
                # Create chat instance with system instructions (not component instruction)
                chat_instance = self._create_chat_instance(
                    self.system_instructions)

                # Build comprehensive prompt that includes:
                # 1. The component mode being activated
                # 2. The original question prompt
                # 3. The specific component instructions
                metadata_block = ""
                metadata_content = context.get('metadata_content') if context else None
                if metadata_content:
                    if isinstance(metadata_content, str):
                        formatted_metadata = metadata_content
                    else:
                        formatted_metadata = json.dumps(
                            metadata_content, indent=2, ensure_ascii=False)
                    metadata_block = f"\nShared Metadata Context:\n{formatted_metadata}\n"

                comprehensive_prompt = f"""Mode: {component_type} Generation

Original Question Prompt: {original_prompt}{metadata_block}

Component Instructions:
{instruction_statement}

Generate the requested {component_type} component following the format specifications."""

                self.request_counter += 1
                if self.min_request_interval > 0:
                    elapsed = time.time() - self._last_request_ts
                    if elapsed < self.min_request_interval:
                        time.sleep(self.min_request_interval - elapsed)
                # record({
                #     'system_instruction': self.system_instructions,
                #     'component_instruction': instruction_statement,
                #     'expected_output': expected_output,
                #     'context': context
                # }, fname=f'request_{self.question_type_slug}_{self.request_counter}',
                #     addresses=('gemini', 'requests'))

                response = chat_instance.send_message(comprehensive_prompt)
                self._last_request_ts = time.time()
                # self._rate_limit_hits = 0 # This line is removed as rpd_flag replaces its functionality

                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")

                # Parse and validate JSON response
                parsed_data = self._parse_json_response(
                    response.text, expected_output)

                # record({
                #     'response_text': response.text,
                #     'parsed': parsed_data,
                #     'context': context
                # }, fname=f'response_{self.question_type_slug}_{self.request_counter}',
                #     addresses=('gemini', 'responses'))

                # Success - log and return
                component_type = context.get('component_type', 'Unknown')
                question_type = context.get('question_type', 'Unknown')
                # print(
                #     f"✅ Generated {prettify(component_type, 'Green')} for {prettify(question_type, 'Yellow')}")

                # Reset RPD flag on success
                if rpd_flag == 1:
                    rpd_flag = 0
                    
                return parsed_data

            except Exception as e:
                error_msg = str(e)
                component_type = context.get('component_type', 'Unknown')
                question_type = context.get('question_type', 'Unknown')

                # Check if this is a 429 RESOURCE_EXHAUSTED error
                is_resource_exhausted = "429 RESOURCE_EXHAUSTED" in error_msg or "RESOURCE_EXHAUSTED" in error_msg

                if is_resource_exhausted:
                    # RPD State Machine Logic
                    if rpd_flag == 0:
                        # First hit: Warning state
                        rpd_flag = 1
                        print(f"⚠️  Rate limit exceeded for {prettify(self.api_key_index, 'Yellow')} "
                              f"({prettify(question_type, 'Yellow')}) waiting {prettify('60s', 'Cyan')}")
                        time.sleep(60)
                        # Retry immediately without incrementing attempt counter
                        continue
                    elif rpd_flag == 1:
                        # Second hit (consecutive): Daily limit exceeded
                        raise RuntimeError(f"⚠️ Request Per Day limit exceeded for {prettify(self.api_key_index, 'Red')}")

                # For real errors, increment attempt counter
                attempt += 1

                # Print error info
                print(f"❌ Attempt {attempt}/{self.max_retries} failed for {prettify(component_type, 'Red')} "
                      f"({prettify(question_type, 'Yellow')}): {error_msg}")

                # If this was the last attempt, raise the error
                if attempt >= self.max_retries:
                    raise RuntimeError(f"Failed to generate component after {self.max_retries} attempts. "
                                       f"Last error: {error_msg}")

                # Wait before retry with exponential backoff for real errors
                wait_time = 2 ** (attempt - 1)
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        # This should never be reached due to the raise in the loop
        raise RuntimeError("Unexpected error in component generation")

    def generate_multiple_components(self, component_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate multiple components in sequence.

        Args:
            component_calls: List of component call dictionaries, each containing:
                - instruction_statement: The instruction for generation
                - expected_output: Expected output format
                - component_type: Type of component (for logging)
                - Other context information

        Returns:
            List of generated component data dictionaries
        """
        generated_components = []

        for i, component_call in enumerate(component_calls):
            component_type = list(component_call.keys())[
                0]  # Get the component type key
            call_data = component_call[component_type]

            print(
                f"🔄 Generating component {i+1}/{len(component_calls)}: {prettify(component_type, 'Cyan')}")

            # Handle both single calls and lists of calls
            if isinstance(call_data, list):
                # Multiple calls for this component type (e.g., metadata with multiple items)
                component_results = []
                for call in call_data:
                    context = {
                        'component_type': component_type,
                        'question_type': call.get('question_type', 'Unknown')
                    }

                    result = self.generate_component(
                        instruction_statement=call['instruction statement'],
                        expected_output=call['output'],
                        context=context
                    )
                    component_results.append(result)

                generated_components.append(
                    {component_type: component_results})
            else:
                # Single call for this component type
                context = {
                    'component_type': component_type,
                    'question_type': call_data.get('question_type', 'Unknown')
                }

                result = self.generate_component(
                    instruction_statement=call_data['instruction statement'],
                    expected_output=call_data['output'],
                    context=context
                )
                generated_components.append({component_type: result})

        return generated_components


# Global generator instance for reuse
_generator_instance = None
_generator_lock = threading.Lock()


def get_gemini_generator(api_key_index: int = 0, question_type: str = None) -> GeminiGenerator:
    """
    Get or create a global Gemini generator instance.

    Args:
        api_key_index: API key index to use
        question_type: Type of question for loading appropriate system instructions

    Returns:
        GeminiGenerator instance
    """
    global _generator_instance

    with _generator_lock:
        if (_generator_instance is None or
            _generator_instance.api_key_index != api_key_index or
                _generator_instance.question_type != question_type):
            _generator_instance = GeminiGenerator(
                api_key_index, question_type=question_type)

    return _generator_instance
