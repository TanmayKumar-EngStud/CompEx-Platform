"""
    main function that creates prompts based on given difficulty pool, then it will make the generate the question data by calling the generate function.
"""
import os
import random
import json
from typing import Any, Optional

from difficulty_pool import get_difficulty_pool
from io_utils import get_json, prettify

from prepare_prompts import PromptPrep
from generator import GenQ

os.system('clear')
os.system('clear')
MOCK_PAPER_LEVEL = 5
exam_definition, qt_info, prompt_component_info = get_json(
    'exam_definition', 'question_type_info', 'prompt_component_info')

prompts_dictionary = {}


def log_stage(exam: str,
              section: Optional[str] = None,
              detail: Optional[str] = None) -> None:
    """Emit a colored progress line showing where generation currently is."""
    segments = [
        f"{prettify('Exam', 'Cyan')}: {prettify(exam, 'Green')}"
    ]
    if section:
        segments.append(
            f"{prettify('Section', 'Cyan')}: {prettify(section, 'Yellow')}"
        )
    if detail:
        segments.append(detail)
    print(" | ".join(segments))


# Sort exams to ensure consistent order (e.g., GMAT before GRE)
sorted_exams = sorted(exam_definition.items(), key=lambda x: x[0])

for exam, sections in sorted_exams:
    log_stage(exam, detail=prettify('Preparing exam structure', 'Blue'))
    prompts_dictionary[exam] = {}
    for section_number, section in sections.items():
        section_name = section['name']
        log_stage(
            exam,
            section_name,
            detail=prettify('Building prompts', 'Magenta')
        )
        n_items = section['total']
        total_prompt_count = 0
        difficulty_list = get_difficulty_pool(
            exam, section_name, n_items+5, MOCK_PAPER_LEVEL)
        # print(f"{exam}: {section_name}:- {difficulty_list} #AVG:- ({sum(difficulty_list)/len(difficulty_list)})")

        # add to dictionary
        prompts_dictionary[exam][section_number] = {}
        prompts_dictionary[exam][section_number]['section'] = section_name
        for question_type in section['question types']:
            log_stage(
                exam,
                section_name,
                detail=f"{prettify('Question type', 'Cyan')}: {prettify(question_type, 'Magenta')}"
            )
            question_type_info = PromptPrep._must_get(qt_info, question_type,
                                                      '@combination-variant.json')
            count_of_this_question_type = section[question_type]
            prompts_dictionary[exam][section_number][question_type] = {
                "has-metadata": question_type_info['has-metadata'],
                'type': question_type_info['type']
            }
            prompts_dictionary[exam][section_number][question_type]['prompts'] = [
            ]
            prompt_count = 0

            while prompt_count < count_of_this_question_type:
                PromptPrep._must_get(section, question_type,
                                     f'section({section_number}) -> {section_name}: @exam_definition.json')

                current_difficulty = difficulty_list.pop()
                nomenclature = question_type_info["nomenclature"]
                prompt = PromptPrep._nomenclature_to_prompt_mapping(
                    nomenclature, question_type, current_difficulty)
                if prompt is None:
                    raise ValueError(
                        f"{prettify('Error:', 'Red', True)} received {prettify('None', 'Magenta')} for {prettify('prompt', 'Yellow')}\nwhere, questionType is {prettify(question_type, 'Magenta')} of {prettify(section_name, 'Magenta')}")

                prompt_buffer: dict[str, Any] = {
                    'prompt': prompt,
                }
                if question_type_info.get('options'):
                    option = question_type_info['options']
                    if isinstance(option, dict):
                        option = random.choices(
                            list(option.keys()), weights=list(option.values()))[0]
                    prompt_buffer['option'] = option
                prompt_count += 1
                # check if it is parent-child or simple question
                if question_type_info.get('child-question', None):
                    prompt_count -= 1
                    # appending 0 because difficulty level was popped for parent question component as well.
                    difficulty_list.append(0)
                    child_count = PromptPrep._get_child_count(
                        nomenclature, question_type=question_type, parent_prompt=prompt, child_info=question_type_info['child-question'])
                    prompt_buffer['child-prompt'] = []
                    for _ in range(child_count):
                        prompt_count += 1
                        child_difficulty = random.randint(
                            max(current_difficulty-1, 1), min(current_difficulty+1, 5))
                        child_question = question_type_info['child-question']
                        child_nomenclature = child_question['nomenclature']
                        child_prompt = PromptPrep._nomenclature_to_prompt_mapping(
                            child_nomenclature, question_type, child_difficulty)
                        child_option = question_type_info['child-question']['options']
                        if isinstance(child_option, dict):
                            try:
                                child_option = random.choices(
                                    list(child_option.keys()), weights=list(child_option.values()))[0]
                            except:
                                raise ValueError(
                                    "this was the child_option that was causing \n")
                        child_prompt_buffer = {
                            'prompt': child_prompt,
                            'option': child_option
                        }
                        prompt_buffer['child-prompt'].append(
                            child_prompt_buffer)
                        difficulty_list.pop()
                if question_type_info.get('has-metadata'):
                    count = question_type_info.get('meta-count', 1)
                    metadata_options_dict = PromptPrep._selective_metadata_info(
                        question_type)
                    if len(metadata_options_dict.keys()) == 0:
                        raise ValueError(
                            f"metadata of {prettify(question_type, 'Yellow')} is getting \n{prettify(json.dumps(metadata_options_dict, indent=2), 'Magenta')}\n as `metadata_options_dict`")
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
                    if not metadata_buffer:
                        raise ValueError(
                            f"metadata_buffer is being empty for {prettify(question_type, 'Red')}")

                    prompt_buffer['metadata-type'] = metadata_buffer

                prompts_dictionary[exam][section_number][question_type]['prompts'].append(
                    prompt_buffer)
            total_prompt_count += prompt_count
        PromptPrep._remove_extra_and_shuffle_created_prompts(
            prompts_dictionary[exam][section_number], total_prompt_count - n_items)
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'log_json_files/prompts_dictionary.json')

with open(file_path, 'w') as json_file:
    json.dump(prompts_dictionary, json_file, indent=3)

paper_gen = GenQ(prompts_dictionary)
paper_gen.generate()
