"""
JSON utility functions for the question generation system.

This module provides centralized JSON processing capabilities that were
previously duplicated across multiple questionComponents files.
"""

import json
import re
import os
from typing import Dict, Any, Optional


# Load character tags mapping once at module level
def _load_tags_mapping() -> Dict[str, str]:
    """Load character tags mapping from tags_char.json."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tags_file = os.path.join(current_dir, 'tags_char.json')
        
        with open(tags_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load tags_char.json: {e}")
        # Return empty dict as fallback
        return {}

# Global tags mapping
TAGS_MAPPING = _load_tags_mapping()


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
        
        # Fix LaTeX mathematical notation that commonly appears in AI responses
        # Convert common LaTeX commands to tagged format for later processing
        latex_replacements = {
            r'\\implies': '<implies>',
            r'\\Rightarrow': '<implies>',
            r'\\rightarrow': '<arrow_right>',
            r'\\leftarrow': '<arrow_left>', 
            r'\\approx': '<approx>',
            r'\\sim': '<sim>',
            r'\\equiv': '<equiv>',
            r'\\cong': '<cong>',
            r'\\sqrt': '<sqrt>',
            r'\\pi': '<pi>',
            r'\\alpha': '<alpha>',
            r'\\beta': '<beta>',
            r'\\gamma': '<gamma>',
            r'\\delta': '<delta>',
            r'\\theta': '<theta>',
            r'\\lambda': '<lambda>',
            r'\\mu': '<mu>',
            r'\\sigma': '<sigma>',
            r'\\phi': '<phi>',
            r'\\omega': '<omega>',
            r'\\infty': '<infinity>',
            r'\\infinity': '<infinity>',
            r'\\times': '<times>',
            r'\\cdot': '<cdot>',
            r'\\div': '<div>',
            r'\\pm': '<pm>',
            r'\\neq': '<ne>',
            r'\\ne': '<ne>',
            r'\\leq': '<le>',
            r'\\le': '<le>',
            r'\\geq': '<ge>',
            r'\\ge': '<ge>',
            r'\\lt': '<lt>',
            r'\\gt': '<gt>',
            r'\\sum': '<sum>',
            r'\\prod': '<prod>',
            r'\\int': '<integral>',
            r'\\partial': '<partial>',
            r'\\nabla': '<nabla>',
            r'\\forall': '<forall>',
            r'\\exists': '<exists>',
            r'\\in': '<in>',
            r'\\subset': '<subset>',
            r'\\superset': '<superset>',
            r'\\cup': '<cup>',
            r'\\cap': '<cap>',
            r'\\union': '<union>',
            r'\\intersection': '<intersection>',
            r'\\emptyset': '<empty_set>',
            r'\\varnothing': '<empty_set>',
            r'\\angle': '<angle>',
            r'\\triangle': '<triangle>',
            r'\\parallel': '<parallel>',
            r'\\perp': '<perp>',
            r'\\therefore': '<therefore>',
            r'\\because': '<because>',
            r'\\iff': '<iff>',
            r'\\Leftrightarrow': '<iff>',
            r'\\lfloor': '<lfloor>',
            r'\\rfloor': '<rfloor>',
            r'\\lceil': '<lceil>',
            r'\\rceil': '<rceil>',
            r'\\langle': '<langle>',
            r'\\rangle': '<rangle>'
        }
        
        # Apply LaTeX replacements
        for latex_cmd, tag in latex_replacements.items():
            text = re.sub(latex_cmd, tag, text)
        
        # Fix problematic characters that can break JSON parsing
        # Replace LaTeX math symbols that might not be properly escaped
        text = text.replace('\\$', '$')  # Fix escaped dollar signs
        text = text.replace('\\\\', '\\')  # Fix double backslashes
        
        # Fix unescaped quotes inside JSON strings
        # This is a basic fix - more sophisticated handling would require proper parsing
        text = re.sub(r'(?<!\\)"([^"]*)"(?=\s*[,}])', r'"\1"', text)

        # Normalize whitespace by joining all lines
        lines = text.split('\n')
        cleaned_text = ''
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_text += cleaned_line + ' '

        cleaned_text = cleaned_text.strip()
        
        # Try to parse the cleaned JSON
        try:
            json.loads(cleaned_text)
            return cleaned_text
        except json.JSONDecodeError:
            return None

    def fix_tags_in_json(json_string: str) -> str:
        """Parse JSON and fix custom tags using tags_char.json mapping."""
        try:
            # Parse the JSON
            data = json.loads(json_string)

            # Recursively replace custom tags in all string values
            def fix_tags_recursive(obj: Any) -> Any:
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        obj[key] = fix_tags_recursive(value)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        obj[i] = fix_tags_recursive(item)
                elif isinstance(obj, str):
                    # Replace all custom tags using the mapping
                    for tag, replacement in TAGS_MAPPING.items():
                        obj = obj.replace(tag, replacement)
                return obj

            # Fix the data and return as formatted JSON
            fixed_data = fix_tags_recursive(data)
            return json.dumps(fixed_data, indent=2, ensure_ascii=False)

        except json.JSONDecodeError as e:
            print(f"JSON parsing failed in fix_tags_in_json: {e}")
            print(f"Problematic JSON string: {json_string[:500]}...")
            return json_string
        except Exception as e:
            print(f"Unexpected error in fix_tags_in_json: {e}")
            return json_string

    # Extract JSON from various formats
    new_text = None

    # Pattern 1: ```json\n...\n```
    markdown_match = re.search(r"```json\s*\n(.*?)\n\s*```", response_text, re.DOTALL)
    if markdown_match:
        try:
            group_text = markdown_match.group(1)
            if group_text and group_text.strip():
                new_text = group_text.strip()
        except (IndexError, AttributeError):
            pass

    # Pattern 2: ```\n{...}\n```
    if not new_text:
        json_block_match = re.search(r"```\s*\n(\{.*?\})\n\s*```", response_text, re.DOTALL)
        if json_block_match:
            try:
                group_text = json_block_match.group(1)
                if group_text and group_text.strip():
                    new_text = group_text.strip()
            except (IndexError, AttributeError):
                pass

    # Pattern 3: Look for JSON object starting with { - use balanced brace matching
    if not new_text:
        # Find the first opening brace
        start_pos = response_text.find('{')
        if start_pos != -1:
            # Count braces to find the matching closing brace
            brace_count = 0
            end_pos = start_pos
            for i, char in enumerate(response_text[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i
                        break
            
            if brace_count == 0:  # Found matching brace
                try:
                    group_text = response_text[start_pos:end_pos + 1]
                    if group_text and group_text.strip():
                        new_text = group_text.strip()
                except Exception:
                    pass

    # Fallback: assume entire response is JSON
    if not new_text:
        new_text = response_text.strip()

    # Clean the JSON string
    new_text = clean_json_string(new_text)
    
    if new_text is None:
        return '{"error": "Failed to parse JSON response"}'

    # Fix custom tags using tags_char.json mapping
    new_text = fix_tags_in_json(new_text)

    # Final validation and formatting with detailed error logging
    try:
        data = json.loads(new_text)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        # Detailed error logging to identify problematic characters
        print(f"FINAL JSON PARSING FAILED: {e}")
        print(f"Error position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
        print(f"Error message: {e.msg if hasattr(e, 'msg') else 'unknown'}")
        
        # Show the problematic area around the error
        if hasattr(e, 'pos') and e.pos is not None:
            start = max(0, e.pos - 50)
            end = min(len(new_text), e.pos + 50)
            problematic_area = new_text[start:end]
            print(f"Problematic area around position {e.pos}:")
            print(f"'{problematic_area}'")
            
            # Try to identify the specific problematic character
            if e.pos < len(new_text):
                problematic_char = new_text[e.pos]
                print(f"Problematic character at position {e.pos}: '{problematic_char}' (ASCII: {ord(problematic_char)})")
        
        print(f"Full response text (first 1000 chars): {new_text[:1000]}")
        return '{"error": "Failed to parse JSON response"}'


def validate_json_format(json_string: str) -> bool:
    """
    Validate that a string is valid JSON.
    
    Args:
        json_string: String to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def is_error_response(message: Dict[str, Any]) -> bool:
    """
    Check if the parsed JSON is an error response from refine_response.
    
    Args:
        message: Parsed JSON dictionary
        
    Returns:
        True if this is an error response, False otherwise
    """
    return isinstance(message, dict) and "error" in message and len(message) == 1


def safe_json_loads(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON string with error handling.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"JSON parsing error: {str(e)}")
        return None


def log_detailed_error(context: str, raw_response: str, error: str, expected_keys: Optional[list] = None) -> None:
    """
    Log detailed error information for debugging.
    
    Args:
        context: Context description for the error
        raw_response: The raw API response that caused the error
        error: Error message or exception details
        expected_keys: Expected JSON keys for validation
    """
    print("=" * 80)
    print(f"DETAILED ERROR LOG - {context}")
    print("=" * 80)
    print(f"Error: {str(error)}")
    print("-" * 40)
    print("RAW RESPONSE:")
    print(raw_response)
    print("-" * 40)
    print(f"Response type: {type(raw_response)}")
    print(f"Response length: {len(raw_response) if raw_response else 0}")
    if expected_keys:
        print(f"Expected keys: {expected_keys}")
    
    # Try to show what refine_response produces
    try:
        refined = refine_response(raw_response)
        print("REFINED RESPONSE:")
        print(refined)
        print("-" * 40)
        
        # Try to parse the refined response
        try:
            parsed = json.loads(refined)
            print("PARSED JSON KEYS:")
            if isinstance(parsed, dict):
                print(list(parsed.keys()))
                print("PARSED JSON CONTENT:")
                for key, value in parsed.items():
                    print(f"  {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            else:
                print(f"Parsed JSON is not a dict, it's: {type(parsed)}")
                print(f"Content: {str(parsed)[:500]}{'...' if len(str(parsed)) > 500 else ''}")
        except Exception as parse_error:
            print(f"FAILED TO PARSE REFINED JSON: {str(parse_error)}")
    except Exception as refine_error:
        print(f"FAILED TO REFINE RESPONSE: {str(refine_error)}")
    
    print("=" * 80)
    print()


# Constants used across the system
JSON_ERROR_WARNING = (
    "\nCRITICAL ERROR: Your response MUST be valid JSON only. "
    "EXAMPLE: {\"solution\": \"text here\"}. No text before/after JSON. "
    "No explanations. No markdown. Just pure JSON that can be parsed by json.loads(). "
    "Use (`) instead of single quotes inside strings."
)

MAX_RETRIES = 3