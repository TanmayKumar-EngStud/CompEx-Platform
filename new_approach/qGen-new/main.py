"""
    
"""
import os
from typing import List, Any
import random
import json
import re

from difficulty_pool import get_difficulty_pool
from io_utils import get_json, prettify
from generator import GenQ

os.system('clear')
os.system('clear')
warn = prettify('⚠️ Warning:', 'Yellow')
sp_char = ['*']
sp = None

exam_definition, qt_info, prompt_component_info = get_json(
    'exam_definition', 'question_type_info', 'prompt_component_info')


def __pick_vocab_level(difficulty: int) -> int:
    weights = {1: [60, 30, 10],
               2: [45, 35, 20],
               3: [30, 40, 30],
               4: [20, 35, 45],
               5: [10, 30, 60]}
    return random.choices([1, 2, 3], weights=weights[difficulty])[0]


def _must_get(d: dict, key: str, source: str) -> dict:
    """Return d[key] or raise respective error"""
    try:
        return d[key]
    except:
        raise ValueError(
            f"{prettify(key, 'Magenta')} missing from {prettify(source,'Cyan')}") from None


def __extract_keywords_from_nomenclature(nomenclature: str) -> List[str]:
    """Return all words found between  < ... >  in order."""
    return re.findall(r'<([^<>]+)>', nomenclature)


def __selective_component_info(prompt_component: str, question_type: str):
    """Returns the list of desired element of that component"""
    def ___fetch_correct_key():
        """Handles special characters in main Key"""
        base = prompt_component
        for sfx in (['']+sp_char):
            key = base + sfx
            if prompt_component_info.get(key, None):
                if sfx in sp_char:
                    sp = sfx
                return key
        raise ValueError(
            f"{prettify('Error:', 'Red', True)} `{prettify(prompt_component, 'Green')}` of {prettify(question_type, 'Magenta')} and it's variants were not found in '{prettify('prompt_component_info.json', 'Cyan')}' file\n ")

    def ___handle_dict_list(selected_component_list: Any):
        """
        it handles prompt_component_list type (both dict and normal list)
            #### if List:
                returns:- list
            #### if Dict:
                returns:- list[dict]
        """
        def ____get_favorable_component_list(items: List[str]) -> List[str]:
            if items is None:
                raise ValueError(
                    f"{prettify('Error: ', 'Red', True)} received 'items': []\nfor{prettify(question_type, 'Magenta')},\n{prettify('prompt_component', 'Yellow')}={prettify(prompt_component, 'Magenta')},\n 'selected_component_list' being\n{prettify(selected_component_list, 'Magenta')}\n\n")
            if sp in [None]:
                try:
                    return [x for x in items if '*' not in x]
                except:
                    raise ValueError(
                        f"{prettify('Error: ', 'Red', True)} received for {prettify(question_type, 'Magenta')},\n{prettify('prompt_component', 'Yellow')}={prettify(prompt_component, 'Magenta')},\n 'selected_component_list' being\n{prettify(selected_component_list, 'Magenta')}\n")

            else:
                return [x for x in items if '*' in x]

        if isinstance(selected_component_list, dict):
            favorable_component_list = ____get_favorable_component_list(
                selected_component_list.keys())
            return {k: selected_component_list[k] for k in favorable_component_list}
        else:
            return ____get_favorable_component_list(selected_component_list)

    prompt_component_found = ___fetch_correct_key()
    prompt_component_list = []
    for prompt_component_options in prompt_component_info[prompt_component_found]:
        if isinstance(prompt_component_options, str):
            raise ValueError(
                f"{prettify('Error:', 'Red',True)}: `prompt_component_options` is being a string: {prettify(prompt_component_options, 'Magenta')}\nThis is happening for question_type: {prettify(question_type, 'Magenta')}\nin file {prettify('prompt_component_info.json', 'Cyan')}\nthe prompt_component_found is:-\n{prettify(prompt_component_found, 'Green')}")
        if prompt_component_options.get('QuestionType', None) is None:
            raise ValueError(
                f"{prettify('Error:', 'Red',True)} {prettify('QuestionType','Yellow')} was not found for Key {prettify(prompt_component_found, 'Magenta')}\nin {prettify('@prompt_component_info.json', 'Cyan')}")
        if question_type in prompt_component_options['QuestionType']:
            prompt_component_list.extend(
                ___handle_dict_list(prompt_component_options['list']))
    return prompt_component_list


def _selective_metadata_info(question_type: str) -> dict:
    """returns dictionary of lists mentioning category of metadata that it is belonging to and the list of content that are available for that question_type"""
    metadataTypes = prompt_component_info['metadataType']
    returning_dict = {}
    for metadata in metadataTypes:
        if question_type in metadata['QuestionType']:
            returning_dict[metadata['category']] = metadata['list']
    return returning_dict


def _nomenclature_to_prompt_mapping(nomenclature: str, question_type: str, difficulty_level: int) -> str:
    """Returns appropriate prompt of that nomenclature"""
    prompt_components = __extract_keywords_from_nomenclature(nomenclature)
    prompt_components[:] = list(
        set(prompt_components) - {'difficulty', 'vocabulary'})

    for prompt_component in prompt_components:
        prompt_component_list = __selective_component_info(
            prompt_component, question_type)
        selected_value = ""
        if isinstance(prompt_component_list, dict):
            selected_choice = random.choice(prompt_component_list.keys())
            sub_choices = prompt_component_list[selected_choice]
            suffix = selected_choice[-1]
            if suffix in sp_char:
                sp = suffix
            selected_value += f"{prompt_component} - {selected_choice}"

            subs = f"sub-{prompt_component}"
            selected_sub_choice = random.choice(sub_choices.keys()) if isinstance(
                sub_choices, dict) else random.choice(sub_choices)
            selected_value += f"> - <{subs} - {selected_sub_choice}"
            while isinstance(sub_choices):
                subs = f"sub-{subs}"
                selected_sub_choice = random.choice(sub_choices.keys()) if isinstance(
                    sub_choices, dict) else random.choice(sub_choices)
                selected_value += f"> - <{subs} - {selected_sub_choice}"
                sub_choices = sub_choices[selected_sub_choice]
            nomenclature = nomenclature.replace(
                prompt_component, selected_value)
        else:
            try:
                selected_value = random.choice(prompt_component_list)
            except:
                raise ValueError(
                    f"\n{prettify('Error: ', 'Red', True)}Received -> \n{prettify(prompt_component_list, 'Magenta')} for {prettify('prompt_component_list', 'Yellow')}\nwhere 'question_type' is {prettify(question_type, 'Red')}\n'prompt_component' is {prettify(prompt_component, 'Magenta')},\nCurrent Nomenclature:\n\t{prettify(nomenclature, 'Red')}")
            nomenclature = nomenclature.replace(
                prompt_component, selected_value)
    nomenclature = nomenclature.replace('<difficulty>', f'<{difficulty_level}>').replace(
        '<vocabulary>', f'<{__pick_vocab_level(difficulty_level)}>')
    return nomenclature
    # now for every exam we are having external data.


def _get_child_count(nomenclature: str, parent_prompt: str, child_info: dict) -> int:
    default_value = 2
    if (child_info.get('child-count', None)):
        return child_info.get('child-count')
    prompt_components = __extract_keywords_from_nomenclature(nomenclature)
    prompt_respective_values = __extract_keywords_from_nomenclature(
        parent_prompt)
    child_question_count = get_json('child_question_count')[0]
    merged_list = list(set(prompt_components) &
                       set(child_question_count.keys()))
    if len(merged_list) > 1:
        print(
            f"{warn} For capturing total child questions for {prettify(question_type, 'Yellow', True)} \n\twith nomenclature :- {prettify(nomenclature, 'Magenta')}\nThese are the {len(merged_list)} identifiers for child-count {prettify(merged_list, 'Red', True)}\nTaking the first one for identification")
    if len(merged_list) == 0:
        # it means these are the parent-child questions with default child count
        return default_value
    identifier = merged_list[0]
    idx = prompt_components.index(identifier)
    selected_prompt_value = prompt_respective_values[idx]
    for options in child_question_count[identifier]:
        if options['value'] == selected_prompt_value:
            return options['count']
    raise ValueError(
        f"{warn} child count for {prettify(identifier, 'Yellow')} : {prettify(selected_prompt_value, 'Magenta')} was not found, issue is in {prettify('child_question_count.json','Cyan')}'s formatting\nThis is the prompt that we got:-\n\t{prettify(prompt, 'Green')}")


def _remove_extra_and_shuffle_created_prompts(section_prompt_dictionary: str, extras: int):
    if extras < 0:
        raise ValueError(
            f"Due to some reason, the total number of prompts generated is being less, received\n\t{prettify('extras', 'Yellow')}: {prettify(extras, 'Red')} for section {prettify(section_prompt_dictionary['section'], 'Red', True)}\ncheck if total count of all total question types is not less then it's respective total in {prettify('exam_definition.json', 'Cyan')}")
    # here we need to find all the prompts that are simple in nature
    # selected_random_question_types =random.choice(section_prompt_dictionary)


prompts_dictionary = {}

for exam, sections in exam_definition.items():
    prompts_dictionary[exam] = {}
    for _idx, section in sections.items():
        section_name = section['name']
        n_items = section['total']
        total_prompt_count = 0
        difficulty_list = get_difficulty_pool(exam, section_name, n_items+5, 2)
        # print(f"{exam}: {section_name}:- {difficulty_list} #AVG:- ({sum(difficulty_list)/len(difficulty_list)})")

        # add to dictionary
        prompts_dictionary[exam][_idx] = {}
        prompts_dictionary[exam][_idx]['section'] = section_name
        for question_type in section['question types']:
            question_type_info = _must_get(qt_info, question_type,
                                           f'@combination-variant.json')
            count_of_this_question_type = section[question_type]
            prompts_dictionary[exam][_idx][question_type] = {
                "has-metadata": question_type_info['has-metadata'],
                'type': question_type_info['type']
            }
            prompts_dictionary[exam][_idx][question_type]['prompts'] = []
            prompt_count = 0
            while prompt_count < count_of_this_question_type:
                count_question_type = _must_get(section, question_type,
                                                f'section({_idx}) -> {section_name}: @exam_definition.json')

                current_difficulty = difficulty_list.pop()
                nomenclature = question_type_info["nomenclature"]
                prompt = _nomenclature_to_prompt_mapping(
                    nomenclature, question_type, current_difficulty)
                if prompt is None:
                    raise ValueError(
                        f"{prettify('Error:', 'Red', True)} received {prettify('None', 'Magenta')} for {prettify('prompt', 'Yellow')}\nwhere, questionType is {prettify(question_type, 'Magenta')} of {prettify(section_name, 'Magenta')}")

                prompt_buffer = {
                    'prompt': prompt,
                }
                if question_type_info.get('options'):
                    option = question_type_info['options']
                    if isinstance(option, dict):
                        option = random.choices(
                            list(option.keys()), weights=option.values())[0]
                    prompt_buffer['option'] = option
                prompt_count += 1
                # check if it is parent-child or simple question
                if question_type_info.get('child-question', None):
                    prompt_count -= 1
                    # appending 0 because difficulty level was popped for parent question component as well.
                    difficulty_list.append(0)
                    child_count = _get_child_count(
                        nomenclature, parent_prompt=prompt, child_info=question_type_info['child-question'])
                    prompt_buffer['child-prompt'] = []
                    for _ in range(child_count):
                        prompt_count += 1
                        child_difficulty = random.randint(
                            max(current_difficulty-1, 1), min(current_difficulty+1, 5))
                        child_question = question_type_info['child-question']
                        child_nomenclature = child_question['nomenclature']
                        child_prompt = _nomenclature_to_prompt_mapping(
                            child_nomenclature, question_type, child_difficulty)
                        child_option = question_type_info['child-question']['options']
                        if isinstance(child_option, dict):
                            try:
                                child_option = random.choices(
                                    list(child_option.keys()), weights=child_option.values())[0]
                            except:
                                raise ValueError(
                                    f"this was the child_option that was causing \n")
                        child_prompt_buffer = {
                            'prompt': child_prompt,
                            'option': child_option
                        }
                        prompt_buffer['child-prompt'].append(
                            child_prompt_buffer)
                        difficulty_list.pop()
                if question_type_info.get('has-metadata'):
                    count = question_type_info.get('meta-count', 1)
                    metadata_options_dict = _selective_metadata_info(
                        question_type)
                    if len(metadata_options_dict.keys()) == 0:
                        raise ValueError(
                            f"metadata of {prettify(question_type, 'Yellow')} is getting \n{prettify(metadata_options_dict, 'Magenta')}\n as `metadata_options_dict`")
                    metadata_buffer = {}

                    for _ in range(count):
                        category = random.choice(list(
                            metadata_options_dict.keys()))

                        if metadata_buffer.get(category, None) is None:
                            metadata_buffer[category] = [
                                random.choice(metadata_options_dict[category])]
                        elif isinstance(metadata_buffer[category], list):
                            metadata_buffer[category].append(
                                random.choice(metadata_options_dict[category])
                            )
                        else:
                            raise ValueError(
                                f"Due to some reason metadata_buffer key is not being a proper list format For,\n\t'question_type': {prettify(question_type, 'Yellow')},\n\t'category': {prettify(category, 'Magenta')}\n we are getting metadata_buffer[category] as\n{prettify(metadata_buffer[category], 'Red')}")
                    if metadata_buffer is {}:
                        raise ValueError(
                            f"metadata_buffer is being empty for {prettify(question_type, 'Red')}")

                    prompt_buffer['metadata-type'] = metadata_buffer

                prompts_dictionary[exam][_idx][question_type]['prompts'].append(
                    prompt_buffer)
            total_prompt_count += prompt_count
        _remove_extra_and_shuffle_created_prompts(
            prompts_dictionary[exam][_idx], total_prompt_count - n_items)
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'log_json_files/prompts_dictionary.json')

with open(file_path, 'w') as json_file:
    json.dump(prompts_dictionary, json_file, indent=3)

paper_gen = GenQ(prompts_dictionary)
paper_gen.generate()
