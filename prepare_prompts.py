import os
from typing import List, Any
import random
import json
import re

from io_utils import get_json, prettify
from generator import GenQ

warn = prettify('⚠️ Warning:', 'Yellow')
sp_char = ['*']
sp = None

exam_definition, qt_info, prompt_component_info = get_json(
    'exam_definition', 'question_type_info', 'prompt_component_info')


class PromptPrep:
    @staticmethod
    def __pick_vocab_level(difficulty: int) -> int:
        weights = {1: [60, 30, 10],
                   2: [45, 35, 20],
                   3: [30, 40, 30],
                   4: [20, 35, 45],
                   5: [10, 30, 60]}
        return random.choices([1, 2, 3], weights=weights[difficulty])[0]

    @staticmethod
    def _must_get(d: dict, key: str, source: str) -> dict:
        """Return d[key] or raise respective error"""
        try:
            return d[key]
        except:
            raise ValueError(
                f"{prettify(key, 'Magenta')} missing from {prettify(source,'Cyan')}") from None

    @staticmethod
    def __extract_keywords_from_nomenclature(nomenclature: str) -> List[str]:
        """Return all words found between  < ... >  in order."""
        return re.findall(r'<([^<>]+)>', nomenclature)

    @staticmethod
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

    @staticmethod
    def _selective_metadata_info(question_type: str) -> dict:
        """returns dictionary of lists mentioning category of metadata that it is belonging to and the list of content that are available for that question_type"""
        metadataTypes = prompt_component_info['metadataType']
        returning_dict = {}
        for metadata in metadataTypes:
            if question_type in metadata['QuestionType']:
                returning_dict[metadata['category']] = metadata['list']
        return returning_dict

    @staticmethod
    def _nomenclature_to_prompt_mapping(nomenclature: str, question_type: str, difficulty_level: int) -> str:
        """Returns appropriate prompt of that nomenclature"""
        prompt_components = PromptPrep.__extract_keywords_from_nomenclature(
            nomenclature)
        prompt_components[:] = list(
            set(prompt_components) - {'difficulty', 'vocabulary'})

        for prompt_component in prompt_components:
            prompt_component_list = PromptPrep.__selective_component_info(
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
            '<vocabulary>', f'<{PromptPrep.__pick_vocab_level(difficulty_level)}>')
        return nomenclature
        # now for every exam we are having external data.

    @staticmethod
    def _get_child_count(nomenclature: str, question_type: str, parent_prompt: str, child_info: dict) -> int:
        default_value = 2
        if (child_info.get('child-count', None)):
            return child_info.get('child-count')
        prompt_components = PromptPrep.__extract_keywords_from_nomenclature(
            nomenclature)
        prompt_respective_values = PromptPrep.__extract_keywords_from_nomenclature(
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
            f"{warn} child count for {prettify(identifier, 'Yellow')} : {prettify(selected_prompt_value, 'Magenta')} was not found, issue is in {prettify('child_question_count.json','Cyan')}'s formatting\nThis is the prompt that we got:-\n\t{prettify(parent_prompt, 'Green')}")

    @staticmethod
    def _remove_extra_and_shuffle_created_prompts(section_prompt_dictionary: str, extras: int):
        if extras < 0:
            raise ValueError(
                f"Due to some reason, the total number of prompts generated is being less, received\n\t{prettify('extras', 'Yellow')}: {prettify(extras, 'Red')} for section {prettify(section_prompt_dictionary['section'], 'Red', True)}\ncheck if total count of all total question types is not less then it's respective total in {prettify('exam_definition.json', 'Cyan')}")
        # here we need to find all the prompts that are simple in nature
        # selected_random_question_types =random.choice(section_prompt_dictionary)
