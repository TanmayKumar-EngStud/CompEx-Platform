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
        if isinstance(generated_data, str) and question_component == 'QuestionSolution':
            _expect(generated_data, str, question_component)
            result['solution'] = generated_data

        else:
            for k, v in generated_data.items():
                if k not in result:
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

    if option_type == 'blank':
        # For Text Completion, options are a list of dictionaries (one per blank)
        # We keep the original structure as requested by the user
        result['options'] = options
        result['answer'] = answer
        return

    if option_type not in ('numeric', 'dichotomous'):
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
        if answer not in options:
            raise ValueError(
                f"{prettify('answer', 'Red')} key {prettify(answer, 'Magenta')} not found in provided options"
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
                f"{prettify('answer', 'Red')} keys {prettify(missing, 'Magenta')} not present in options"
            )
        # Store answer as list of label strings
        result['answer'] = answer

    elif option_type == 'blank':
        pass
        # have to write code for this one.

    elif option_type == 'dichotomous':
        # For Table Analysis: options is list of statements, answer is dict {statement: bool}
        if not isinstance(options, list):
            raise TypeError(
                f"{prettify('options', 'Yellow')} must be {prettify('list', 'Green')} for dichotomous questions; got {prettify(type(options).__name__, 'Red')}"
            )
        if not isinstance(answer, dict):
            raise TypeError(
                f"{prettify('answer', 'Yellow')} must be {prettify('dict', 'Green')} for dichotomous questions; got {prettify(type(answer).__name__, 'Red')}"
            )
        
        # Validate answer keys match options
        # Note: In some cases, answer might be partial or full, but ideally should cover all options
        # For now, we just ensure answer keys are in options
        unknown_keys = [k for k in answer.keys() if k not in options]
        if unknown_keys:
             raise ValueError(
                f"{prettify('answer', 'Red')} keys {prettify(unknown_keys, 'Magenta')} not found in options list"
            )
        
        result['options'] = options
        result['answer'] = answer

    elif option_type == 'numeric':
        # For numeric entry, there are no options, just an answer
        if answer is None:
             raise ValueError(f"Answer is missing for numeric question type")
        result['answer'] = answer
