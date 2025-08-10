"""
This file handles all the question components, how they are needed to be managed based on question component type.
"""
from ast import Pass
from typing import Literal, Union, Any, get_args

from regex import T
from io_utils import prettify
import random
import json


def _expect(obj: Any, expected: type, label: str) -> None:
    obj_print = obj if isinstance(obj, str) else json.dumps(obj, indent=2)
    if not isinstance(obj, expected):
        raise TypeError(
            f"{prettify(label, 'Yellow')} must be {prettify(expected.__name__, 'Green')}; got {prettify(type(obj).__name__, 'Red')}\n{obj.__name__} = {prettify(obj_print, 'Magenta')}")


def manage_generated_content(result: dict, question_type: str, question_component: str, generated_data: Union[str, dict], option_type: str = None):
    if question_component in ('QuestionMetadata', 'QuestionOptions/Answer'):
        _expect(generated_data, dict, question_component)
        return (
            manage_metadata_content(result, question_type, generated_data) if question_component == 'QuestionMetadata' else
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


def manage_metadata_content(result: dict, question_type: str, generated_data: dict):
    if len(generated_data) != 1:
        print(
            f"Error: found more than one key in manage_metadata_content this situation is not handled : {prettify(list(generated_data.keys()), 'Red', True)}")
        raise ValueError(
            f"Expected exactly one key, got {list(generated_data.keys())}")
    key, value = next(iter(generated_data.items()))
    metadata = result.setdefault('metadata', {})
    if key == 'para':
        metadata['Passage'] = metadata.get('Passage', '') + f'\n{value}'
    else:
        metadata.setdefault(key, []).append(value)


OptionType = Literal['blank', 'single', 'multi']


def manage_options_answer_content(result: dict, question_type: str, generated_data: Union[str, dict], option_type: str):
    if option_type not in get_args(OptionType):
        raise ValueError(
            f"Give option_type is not correct got {prettify(option_type, 'Red')} for question-type: {prettify(question_type, 'Yellow')}")

    if option_type == 'single':
        # need to handle Data Sufficiency type here
        result['answer'] = generated_data['options'][generated_data['answer']]
        result['options'] = random.shuffle(
            list(generated_data['options'].values()))

    elif option_type == 'multi':
        result['answer'] = list(generated_data['options'][ans]
                                for ans in generated_data['answer'])
        result['options'] = random.shuffle(
            list(generated_data['options'].values()))

    elif option_type == 'blank':
        pass
        # have to write code for this one.
