"""
This file handles all the question components, how they are needed to be managed based on question component type.
"""
from typing import Literal, Union, Any, get_args
from io_utils import prettify
import json

OptionType = Literal['blank', 'single', 'multi', 'numeric', 'dichotomous']

def _expect(obj: Any, expected: type, label: str) -> None:
    """
        validates and returns the expected data values, throws error if it is incorrect.
    """
    obj_print = obj if isinstance(obj, str) else json.dumps(obj, indent=2)
    if not isinstance(obj, expected):
        raise TypeError(
            f"{prettify(label, 'Yellow')} must be {prettify(expected.__name__, 'Green')}; got {prettify(type(obj).__name__, 'Red')}\n{obj.__name__} = {prettify(obj_print, 'Magenta')}")

def manage_generated_content(result: dict, question_type: str, question_component: str, generated_data: Union[str, dict], option_type: str = None, source_info: dict = None):
    """
        Manages to arrange all the question components individually to be stored in the correct key of the `result`
        
        Args:
            source_info: Optional dict containing MSR source metadata (source_number, source_type, focused_skill)
    """
    if question_component in ('QuestionMetadata', 'QuestionOptions/Answer'):
        _expect(generated_data, dict, question_component)
        return (
            manage_metadata_content(result, question_type, generated_data, source_info) if question_component == 'QuestionMetadata' else
            manage_options_answer_content(
                result, question_type, generated_data, option_type)
        )
    else:
        if question_component == 'QuestionSolution':
            # Handle both string (old) and dict (new) formats for robustness
            if isinstance(generated_data, str):
                _expect(generated_data, str, question_component)
                result['solution'] = generated_data
            elif isinstance(generated_data, dict):
                 # Sanitization: Extract only the 'solution' part, ignore 'scratchpad'
                 result['solution'] = generated_data.get('solution', '')

            else:
                 raise TypeError(f"QuestionSolution expected str or dict, got {type(generated_data)}")

        elif question_component == 'QuestionBlueprint':
            # Store blueprint as is (could be dict or string)
            # result['blueprint'] = generated_data
            pass # we won't be storing the blueprint

        else:
            for k, v in generated_data.items():
                # PATCH: Flatten list if model returns list for question/solution
                if k in ['question', 'solution', 'title'] and isinstance(v, list) and v:
                     import random
                     v = random.choice(v)

                if k not in result:
                    result[k] = v
                else:
                    # Prevent appending for singular fields
                    if k in ['question', 'solution', 'answer', 'difficulty', 'title']:
                        result[k] = v
                    else:
                        result[k] = [result[k]] if not isinstance(
                            result[k], list) else result[k]
                        result[k].append(v)

def manage_metadata_content(result: dict, question_type: str, generated_data: dict, source_info: dict = None):
    """
        Manages all the question metadata components to be stored with the correct key for `result` <br>it handles [Passage, Graph, Tables]; <br>`Graphs` and `Tables` are stored directly.
        
        Args:
            source_info: Optional dict with 'source_number' for MSR questions
    """
    metadata = result.setdefault('metadata', {})
    
    # Special handling for Multi-Source Reasoning
    if question_type == 'Multi-Source Reasoning' and source_info and 'source_number' in source_info:
        source_num = source_info['source_number']
        source_key = f"Source{source_num}"
        
        # Store entire generated_data under Source1/2/3
        metadata[source_key] = generated_data
    else:
        # Standard metadata handling
        for key, value in generated_data.items():
            if key == 'para' or key == 'passage':
                existing = metadata.get('Passage', '')
                separator = '\n' if existing else ''
                metadata['Passage'] = f"{existing}{separator}{value}"
            elif key == 'statements':
                if not isinstance(value, list):
                    raise TypeError(
                        f"{prettify('statements', 'Yellow')} must be a list; got {prettify(type(value).__name__, 'Red')}")
                metadata['Statements'] = value
            else:
                metadata.setdefault(key, []).append(value)

def manage_options_answer_content(result: dict, question_type: str, generated_data: Union[str, dict], option_type: str):
    """
        Manages all the question options and answers with the correct key for `result`<br>Currently handling option type `single`, `multi`
    """
    if option_type not in get_args(OptionType):
        raise ValueError(
            f"Give option_type is not correct got {prettify(option_type, 'Red')} for question-type: {prettify(question_type, 'Yellow')}")

    options = generated_data.get('options')
    answer = generated_data.get('answer')

    ds_default_options = {
        "A": "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.",
        "B": "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient.",
        "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient.",
        "D": "EITHER statement ALONE is sufficient.",
        "E": "Statements (1) and (2) TOGETHER are NOT sufficient."
    }

    # Handle new strict schema format (options_list)
    options_list = generated_data.get('options_list')
    if options_list:
        if option_type == 'blank':
             # For blank, values is a list
             options = {item['key']: item['values'] for item in options_list}
        else:
             # For single/multi, value is a string
             options = {item['key']: item['value'] for item in options_list}
    
    if option_type == 'blank':
        # For Text Completion, options are a list of dictionaries (one per blank)
        # We keep the original structure as requested by the user
        result['options'] = options
        result['answer'] = answer
        return

    if option_type not in ('numeric', 'dichotomous', 'blank'):
        if options is None and question_type == 'Data Sufficiency':
            options = ds_default_options.copy()
        if not isinstance(options, dict):
            raise TypeError(
                f"{prettify('options', 'Yellow')} must be {prettify('dict', 'Green')}; got {prettify(type(options).__name__, 'Red')}"
            )

        # Keep options as dictionary (Standardized Format)
        result['options'] = options

    if option_type == 'single':
        if not isinstance(answer, str):
            raise TypeError(
                f"{prettify('answer', 'Yellow')} must be {prettify('str', 'Green')} for single-choice questions; got {prettify(type(answer).__name__, 'Red')}"
            )
        
        # Fuzzy Logic: Check if answer is a KEY (e.g., 'A') or VALUE (e.g., '5')
        if answer not in options:
            # Try to find the key by matching the value
            found_key = None
            for key, value in options.items():
                # Check for exact string match or numeric match
                if str(value).strip() == str(answer).strip():
                    found_key = key
                    break
                # Try numeric match (e.g., 49.50 vs 49.5)
                try:
                    if float(str(value).strip()) == float(str(answer).strip()):
                        found_key = key
                        break
                except ValueError:
                    pass
            
            if found_key:
                 # Correct the answer to be the key
                 answer = found_key
            else:
                # Check if answer is a value instead of a key (e.g. 200 instead of 'C')
                found_key_by_value = None
                for k, v in options.items():
                    if str(v).strip() == str(answer).strip():
                        found_key_by_value = k
                        break
                
                if found_key_by_value:
                    answer = found_key_by_value
                else:
                    raise ValueError(
                        f"{prettify('answer', 'Red')} key {prettify(answer, 'Magenta')} not found in provided options.\nAvailable Options: {prettify(json.dumps(options, indent=2), 'Yellow')}"
                    )
        
        # Store answer as simple label string
        result['answer'] = answer

    elif option_type == 'multi':
        if not isinstance(answer, list):
            raise TypeError(
                f"{prettify('answer', 'Yellow')} must be {prettify('List[str]', 'Green')} for multi-select questions; got {prettify(type(answer).__name__, 'Red')}"
            )
        missing = [key for key in answer if key not in options]
        if missing:
            raise ValueError(
                f"{prettify('answer', 'Red')} keys {prettify(missing, 'Magenta')} not present in options.\nAvailable Options: {prettify(list(options.keys()), 'Yellow')}"
            )
        # Store answer as list of label strings
        result['answer'] = answer

    elif option_type == 'blank':
        # For Text Completion, options can be a dict (TC-1) or list of dicts (TC-2/3)
        if not isinstance(options, (dict, list)):
             raise TypeError(
                f"{prettify('options', 'Yellow')} must be {prettify('dict or list', 'Green')} for blank questions; got {prettify(type(options).__name__, 'Red')}"
            )
        result['options'] = options
        result['answer'] = answer

    elif option_type == 'dichotomous':
        # For Table Analysis: options is list of statements, answer is dict {statement: bool}
        
        # Handle user-defined schema format where answer is a list of objects
        if isinstance(answer, list):
             # Convert list of objects back to dict {statement: response}
             # Assuming list items are dicts with 'statement' and 'response' keys
             try:
                # Check structure: strict schema often returns list of 'statement' and 'response'
                if answer and isinstance(answer[0], dict) and 'statement' in answer[0]:
                    answer = {item['statement']: item['response'] for item in answer}
                # Fallback: if it's just a list of boolean/string values, try to map to options by index
                elif len(answer) == len(options):
                     answer = {opt: ans for opt, ans in zip(options, answer)}
             except (KeyError, TypeError) as e:
                 # If automatic conversion fails, log but proceed to strict check which will raise error
                 pass

        if not isinstance(options, list):
            raise TypeError(
                f"{prettify('options', 'Yellow')} must be {prettify('list', 'Green')} for dichotomous questions; got {prettify(type(options).__name__, 'Red')}"
            )
        if not isinstance(answer, dict):
            raise TypeError(
                f"{prettify('answer', 'Yellow')} must be {prettify('dict', 'Green')} for dichotomous questions; got {prettify(type(answer).__name__, 'Red')}"
            )
        
        # Validate answer keys match options (Fuzzy Match for Dichotomous Keys)
        unknown_keys = [k for k in answer.keys() if k not in options]
        if unknown_keys:
             # Try fuzzy matching keys (e.g. slight text variations)
             corrected_answer = {}
             for ans_key, ans_val in answer.items():
                 found_opt = None
                 if ans_key in options:
                     found_opt = ans_key
                 else:
                     # Simple fuzzy match: check if one string contains the other or levenshtein-ish
                     # This handles cases where model slightly alters the statement text
                     for opt in options:
                         if opt in ans_key or ans_key in opt: # Substring match
                             found_opt = opt
                             break
                 
                 if found_opt:
                     corrected_answer[found_opt] = ans_val
                 else:
                     # If still not found, keep original logging
                     pass
             
             if len(corrected_answer) == len(answer):
                 answer = corrected_answer
             else:
                 # Re-check unknowns after fuzzy correction
                 unknown_keys = [k for k in answer.keys() if k not in options]
                 if unknown_keys:
                    raise ValueError(
                        f"{prettify('answer', 'Red')} keys {prettify(unknown_keys, 'Magenta')} not found in options list.\nAvailable Options: {prettify(json.dumps(options, indent=2), 'Yellow')}"
                    )
        
        result['options'] = options
        result['answer'] = answer

    elif option_type == 'numeric':
        # Numerical Entry: Answer is a number, no options validation needed
        # Ensure answer is convertable to float/int
        try:
            if isinstance(answer, (int, float)):
                 pass
            elif isinstance(answer, str):
                 # Try to parse if string
                 float(answer.strip().replace(',', ''))
            else:
                 pass # Allow it, but maybe warn?
        except ValueError:
             raise ValueError(f"{prettify('answer', 'Red')} for Numerical Entry must be a number, got {prettify(answer, 'Magenta')}")
        
        result['options'] = None # No options for numerical entry
        result['answer'] = answer