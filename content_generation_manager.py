"""
This file handles all the question components, how they are needed to be managed based on question component type.
"""
from typing import Literal, Union, Any, get_args
from io_utils import prettify
import json

OptionType = Literal['blank', 'single', 'multi', 'numeric', 'dichotomous']

def normalize_generated_data(data: Any, question_component: str, question_type: str) -> Any:
    """
    Proactively fixes common structural issues in model output 
    BEFORE strict validation occurs. This reduces retries for 
    technically-valid but structurally-misaligned data.
    """
    if not isinstance(data, dict):
        return data

    # 1. Structural Recovery (Parent-to-Child)
    # If it's a child but model returned parent structure
    child_trigger_keys = ['child-questions', 'questions', 'child_questions']
    for ck in child_trigger_keys:
        if ck in data and isinstance(data[ck], list) and data[ck]:
            # If root is missing core component data but it's nested in children
            if question_component == 'QuestionOptions/Answer' and 'options' not in data and 'answer' not in data:
                # Search for any child that HAS the component data
                for candidate in data[ck]:
                    if isinstance(candidate, dict) and ('options' in candidate or 'answer' in candidate):
                        return normalize_generated_data(candidate, question_component, question_type)
            
            # For QuestionText/Solution, same logic
            if question_component in ['QuestionText', 'QuestionSolution', 'QuestionTitle']:
                target_key = 'question' if question_component == 'QuestionText' else \
                             'solution' if question_component == 'QuestionSolution' else 'title'
                if target_key not in data:
                    for candidate in data[ck]:
                        if isinstance(candidate, dict) and target_key in candidate:
                            return normalize_generated_data(candidate, question_component, question_type)

    # 2. Wrapper Unwrapping
    wrappers = ['response', 'data', 'result', 'question_data', 'content']
    for wk in wrappers:
        if wk in data and len(data) == 1 and isinstance(data[wk], dict):
            return normalize_generated_data(data[wk], question_component, question_type)

    # 3. List-to-Dict Options Conversion (with detailed mapping)
    if 'options' in data and isinstance(data['options'], list):
        import string
        labels = list(string.ascii_uppercase)
        raw_options = data['options']
        new_options = {}
        for i, val in enumerate(raw_options):
            if i >= len(labels): break
            key = labels[i]
            if isinstance(val, dict) and 'text' in val:
                # Already mostly correct, ensure explanation exists
                new_options[key] = {
                    "text": str(val.get('text', '')),
                    "explanation": str(val.get('explanation', ''))
                }
            else:
                # Convert string (or other) to detailed format seen in simple questions
                new_options[key] = {
                    "text": str(val),
                    "explanation": f"The model provided this as option {key}."
                }
        data['options'] = new_options
    
    return data

def _expect(obj: Any, expected: type, label: str, question_type: str = None, exam_type: str = None, file_name: str = None) -> None:
    """
        validates and returns the expected data values, throws error if it is incorrect.
    """
    obj_print = obj if isinstance(obj, str) else json.dumps(obj, indent=2)
    if not isinstance(obj, expected):
        context = ""
        if question_type and exam_type:
            context = f" in {prettify(question_type, 'Magenta')} for {prettify(exam_type, 'Cyan')}"
        
        detail = ""
        if file_name:
            detail = f" (Component: {prettify(label, 'Yellow')}, File: {prettify(file_name, 'Green')})"
        
        raise TypeError(
            f"{prettify(label, 'Yellow')} must be {prettify(expected.__name__, 'Green')}; got {prettify(type(obj).__name__, 'Red')}{context}{detail}\nData = {prettify(obj_print, 'Magenta')}")

def manage_generated_content(result: dict, question_type: str, question_component: str, generated_data: Union[str, dict], option_type: str = None, source_info: dict = None, exam_type: str = None, file_name: str = None):
    """
        Manages to arrange all the question components individually to be stored in the correct key of the `result`
        
        Args:
            source_info: Optional dict containing MSR source metadata (source_number, source_type, focused_skill)
    """
    # Proactive structural normalization
    generated_data = normalize_generated_data(generated_data, question_component, question_type)

    if question_component in ('QuestionMetadata', 'QuestionOptions/Answer'):
        _expect(generated_data, dict, question_component, question_type, exam_type, file_name=file_name)
        return (
            manage_metadata_content(result, question_type, generated_data, source_info, exam_type=exam_type, file_name=file_name) if question_component == 'QuestionMetadata' else
            manage_options_answer_content(
                result, question_type, generated_data, option_type, exam_type=exam_type, file_name=file_name)
        )
    else:
        if question_component == 'QuestionSolution':
            # Handle both string (old) and dict (new) formats for robustness
            if isinstance(generated_data, str):
                _expect(generated_data, str, question_component, question_type, exam_type, file_name=file_name)
                result['solution'] = generated_data
            elif isinstance(generated_data, dict):
                 # Sanitization: Extract only the 'solution' part, ignore 'scratchpad'
                 result['solution'] = generated_data.get('solution', '')

            else:
                 raise TypeError(f"QuestionSolution expected str or dict, got {type(generated_data).__name__} in {prettify(question_type, 'Magenta')} for {prettify(exam_type, 'Cyan')} (File: {prettify(file_name, 'Green')})\nData = {prettify(json.dumps(generated_data, indent=2) if not isinstance(generated_data, str) else generated_data, 'Magenta')}")


        else:
            _expect(generated_data, dict, question_component, question_type, exam_type, file_name=file_name)
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

def manage_metadata_content(result: dict, question_type: str, generated_data: dict, source_info: dict = None, exam_type: str = None, file_name: str = None):
    """
        Manages all the question metadata components to be stored with the correct key for `result` <br>it handles [Passage, Graph, Tables]; <br>`Graphs` and `Tables` are stored directly.
        
        Args:
            source_info: Optional dict with 'source_number' for MSR questions
    """
    metadata = result.setdefault('metadata', {})
    _expect(generated_data, dict, 'QuestionMetadata', question_type, exam_type, file_name=file_name)

    # Special handling for Multi-Source Reasoning
    if question_type == 'Multi-Source Reasoning' and source_info and 'source_number' in source_info:
        source_num = source_info['source_number']
        source_key = f"Source{source_num}"
        
        # Store entire generated_data under Source1/2/3
        metadata[source_key] = generated_data
    else:
        # Standard metadata handling
        for key, value in generated_data.items():
            # Avoid nesting a key named 'metadata' inside the metadata dict
            if key == 'metadata':
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                             manage_metadata_content(result, question_type, item, source_info)
                        else:
                             metadata.setdefault('info', []).append(item)
                elif isinstance(value, dict):
                    manage_metadata_content(result, question_type, value, source_info)
                continue

            if key == 'para' or key == 'passage':
                existing = metadata.get('Passage', '')
                separator = '\n' if existing else ''
                metadata['Passage'] = f"{existing}{separator}{value}"
            elif key == 'statements':
                if not isinstance(value, list):
                    raise TypeError(
                        f"{prettify('statements', 'Yellow')} must be a list in {prettify(question_type, 'Magenta')} for {prettify(exam_type or 'Unknown Exam', 'Cyan')} (File: {prettify(file_name, 'Green')}); got {prettify(type(value).__name__, 'Red')}")
                metadata['Statements'] = value
            elif key in ['question', 'options', 'answer', 'solution']:
                # For Table Analysis and some IR types, the model returns these in metadata.
                # We should store them in the top-level result instead of burying them in metadata.
                if key not in result or not result[key]:
                    result[key] = value
            else:
                # Store other keys. If it's a single item (like Table), don't always wrap in list
                # unless there's already something there.
                if key not in metadata:
                    metadata[key] = value
                else:
                    if not isinstance(metadata[key], list):
                        metadata[key] = [metadata[key]]
                    metadata[key].append(value)

def manage_options_answer_content(result: dict, question_type: str, generated_data: Union[str, dict], option_type: str, exam_type: str = None, file_name: str = None):
    """
        Manages all the question options and answers with the correct key for `result`<br>Currently handling option type `single`, `multi`
    """
    if option_type not in get_args(OptionType):
        raise ValueError(
            f"Give option_type is not correct got {prettify(option_type, 'Red')} for question-type: {prettify(question_type, 'Yellow')}")

    options = generated_data.get('options')
    answer = generated_data.get('answer')
    explanations = generated_data.get('explanations')

    ds_default_options = {
        "A": "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.",
        "B": "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient.",
        "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient.",
        "D": "EITHER statement ALONE is sufficient.",
        "E": "Statements (1) and (2) TOGETHER are NOT sufficient."
    }

    if explanations:
        result['explanations'] = explanations

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
        # Defensive Check: If options is None, check for 'explanations' (common in DS/other types)
        if options is None and isinstance(generated_data, dict):
             options = generated_data.get('explanations')

        if options is None and question_type == 'Data Sufficiency':
            options = ds_default_options.copy()
        
        if options is None:
             raise ValueError(f"{prettify('options', 'Yellow')} missing in generated data for {prettify(question_type, 'Magenta')} in {prettify(exam_type or 'Unknown Exam', 'Cyan')} (File: {prettify(file_name, 'Green')})\nData = {prettify(json.dumps(generated_data, indent=2), 'Magenta')}")

        _expect(options, dict, 'options', question_type, exam_type, file_name=file_name)

        # Keep options as dictionary (Standardized Format)
        result['options'] = options

    if option_type == 'single':
        _expect(answer, str, 'answer', question_type, exam_type, file_name=file_name)
        
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
                        f"{prettify('answer', 'Red')} key {prettify(answer, 'Magenta')} not found in provided options in {prettify(question_type, 'Magenta')} for {prettify(exam_type, 'Cyan')} (File: {prettify(file_name, 'Green')}).\nAvailable Options: {prettify(json.dumps(options, indent=2), 'Yellow')}\nFull Data: {prettify(json.dumps(generated_data, indent=2), 'Magenta')}"
                    )
        # Store answer as simple label string
        result['answer'] = answer

    elif option_type == 'multi':
        _expect(answer, list, 'answer', question_type, exam_type, file_name=file_name)
        missing = [key for key in answer if key not in options]
        if missing:
            raise ValueError(
                f"{prettify('answer', 'Red')} keys {prettify(missing, 'Magenta')} not present in options in {prettify(question_type, 'Magenta')} for {prettify(exam_type, 'Cyan')} (File: {prettify(file_name, 'Green')}).\nAvailable Options: {prettify(list(options.keys()), 'Yellow')}\nFull Data: {prettify(json.dumps(generated_data, indent=2), 'Magenta')}"
            )
        # Store answer as list of label strings
        result['answer'] = answer

    elif option_type == 'blank':
        # For Text Completion, options can be a dict (TC-1) or list of dicts (TC-2/3)
        _expect(options, (dict, list), 'options', question_type, exam_type, file_name=file_name)
        _expect(answer, list, 'answer', question_type, exam_type, file_name=file_name)
        result['options'] = options
        result['answer'] = answer

    elif option_type == 'dichotomous':
        # For Table Analysis/MSR: options is dict (statement + explanation), answer is mapping dict {statement: response}
        
        # 1. Normalize Answer Format
        if isinstance(answer, list):
             if answer and isinstance(answer[0], dict):
                  # If model returned [{"Stmt": "Yes", ...}], merge them or take the first if it's the mapping object
                  if len(answer) == 1:
                       answer = answer[0]
                  else:
                       # Merge multiple mapping objects if returned (unlikely but safe)
                       new_answer = {}
                       for item in answer:
                            new_answer.update(item)
                       answer = new_answer
        
        # 2. Extract Valid Statements for Key Verification
        valid_statements = []
        if isinstance(options, dict):
            for key, val in options.items():
                if isinstance(val, dict) and 'text' in val:
                    valid_statements.append(val['text'])
                else:
                    valid_statements.append(str(val))
        elif isinstance(options, list):
            valid_statements = options

        _expect(options, (dict, list), 'options', question_type, exam_type, file_name=file_name)
        _expect(answer, dict, 'answer', question_type, exam_type, file_name=file_name)
        
        # 3. Validate answer keys match statement texts
        unknown_keys = [k for k in answer.keys() if k not in valid_statements]
        if unknown_keys:
             corrected_answer = {}
             for ans_key, ans_val in answer.items():
                 found_stmt = None
                 if ans_key in valid_statements:
                     found_stmt = ans_key
                 else:
                     # Fuzzy Match
                     for stmt in valid_statements:
                         if stmt in ans_key or ans_key in stmt:
                             found_stmt = stmt
                             break
                 
                 if found_stmt:
                     corrected_answer[found_stmt] = ans_val
             
             if len(corrected_answer) == len(answer):
                 answer = corrected_answer
             else:
                  unknown_keys = [k for k in answer.keys() if k not in valid_statements]
                  if unknown_keys:
                      raise ValueError(
                          f"{prettify('answer', 'Red')} mapping keys {prettify(unknown_keys, 'Magenta')} not found in options statements for {prettify(question_type, 'Magenta')} in {prettify(exam_type, 'Cyan')} (File: {prettify(file_name, 'Green')}).\nValid Statements: {prettify(valid_statements, 'Yellow')}"
                      )
        
        result['options'] = options
        result['answer'] = answer

    elif option_type == 'numeric':
        # Numerical Entry: Answer is a number, no options validation needed
        try:
            if not isinstance(answer, (int, float)):
                 # Try to parse if string
                 float(str(answer).strip().replace(',', ''))
        except (ValueError, TypeError):
             raise ValueError(f"{prettify('answer', 'Red')} for Numerical Entry must be a number in {prettify(question_type, 'Magenta')} for {prettify(exam_type or 'Unknown Exam', 'Cyan')}; got {prettify(answer, 'Magenta')}")
        
        result['options'] = None # No options for numerical entry
        result['answer'] = answer