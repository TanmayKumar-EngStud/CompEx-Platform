"""
Here we will get complete prompt dictionary, we will traverse from every question prompt, generate their respective question components as per given in `question_component_types.json`.
"""

from io_utils import get_json, prettify, get_Component_Template, record
from api_utils import get_gemini_generator
import os
import json
import threading
# import concurrent.futures
from typing import Dict, Any, List
from content_generation_manager import manage_generated_content

all_question_structure = get_json('question_component_types')[0]


class GenQ:
    def __init__(self, prompts_dictionary: dict) -> None:
        self.prompts_dictionary = prompts_dictionary

    def get_question_data(self, prompt_details):
        """
        1. Generates question call wise {'instruction statements', 'output' types}
        2. for every call wise, we will use generate function,
        3. if that specific question-type is having any wrapper format for any specific question component, the fetched data is then wrapped in that envelope.
        4. returns the complete question data of that component.

            Args:

                {
                    'type': 'simple'/'parent'/'child',
                    'exam': 'GRE'/'GMAT'/etc.,
                    'section': 'Verbal'/'Quants',
                    'question-type': 'Data Sufficiency'/'Reading Comprehension',
                    'option': 'blank'/'single'/'multi',
                    'prompt': prompt_data['prompt']
                }

            Returns:

                complete question of that prompt with values of question components.
        """
        rand_var = None
        if prompt_details['question-type'] == 'Text Completion':
            rand_var = prompt_details['prompt'].split(' - ', 1)[0].strip('<>')
        component_instruction = all_question_structure[1]
        question_components = list(
            all_question_structure[0][prompt_details.get('type', 'child')])
        question_type = prompt_details['question-type']
        if not prompt_details.get('metadata-type', None):
            if 'QuestionMetadata' in question_components:
                question_components.remove('QuestionMetadata')
        # if prompt_details.get('type') is None:
        #     # only child prompts are not having 'type'
        #     prompt_details['type'] = 'child'
        prefix = '' if prompt_details['type'] == 'simple' else prompt_details['type']

        # region fetching raw templates
        component_calls = []
        for question_component in question_components:
            component_call_buffer = {}

            if question_component == 'ChildQuestions':
                continue
            elif question_component == "QuestionMetadata":
                component_call_buffer[question_component] = []
                prompt_metadata_types = list(
                    prompt_details['metadata-type'].keys())
                for prompt_metadata_type in prompt_metadata_types:
                    if prompt_metadata_type == 'passage':
                        for prompt_metadata_item in prompt_details['metadata-type'][prompt_metadata_type]:
                            count_number_of_passages = len(
                                prompt_details.get('child-prompt', 1))  # added 1 as default for Critical Reasoning question passage.
                            file_name = component_instruction[question_component][prompt_metadata_type]['file-name']
                            variables = component_instruction[question_component][prompt_metadata_type]['variables']
                            for para_no in range(1, count_number_of_passages+1):
                                component_call_buffer[question_component].append({
                                    "instruction statement": f"Generate para {para_no} of {count_number_of_passages}:\n{get_Component_Template(question_component, file_name, prompt_details['exam'], prompt_details['section'], prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var = rand_var)}",
                                    "output": component_instruction[question_component][prompt_metadata_type]['output']
                                })
                    else:
                        component_call_buffer[question_component] = []
                        for prompt_metadata_item in prompt_details['metadata-type'][prompt_metadata_type]:
                            """prompt_metadata_item = 'data_table' or 'area_chart' or 'pie_chart' """
                            file_name = component_instruction[question_component][prompt_metadata_type]['file-name']
                            variables = component_instruction[question_component][prompt_metadata_type]['variables']
                            component_call_buffer[question_component].append(
                                {
                                    "instruction statement": get_Component_Template(question_component, file_name, prompt_details['exam'], prompt_details['section'], prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var=rand_var),
                                    "output": component_instruction[question_component][prompt_metadata_type]['output'],
                                    'file-name': file_name
                                }
                            )
            # Metadata component is being handled (I guess) moving forward for now. {Data Sufficiency type of content is still left.}
            # We need to add another else if block for handling question options as well.
            elif question_component == "QuestionOptions/Answer":
                component_call_buffer = {}
                for category_list in component_instruction.get(question_component):
                    if category_list.get('type', None) == None:
                        raise ValueError(
                            f"{prettify(question_component, 'Yellow')} is not having {prettify('type', 'Red')} in one of it's provided item")
                    if prompt_details.get('option', None) is None:
                        raise ValueError(
                            f"The current questionType: {prettify(prompt_details['question-type'], 'Yellow')} is not having the `{prettify('option', 'Red')}` provided with prompt, for question_component: {prettify(prefix+question_component, 'Red', True)} here are the prompt details:\n{prettify(prompt_details, 'Blue')}")
                    if prompt_details['option'] == category_list['type'] and prompt_details['question-type'] in category_list['QuestionType']:
                        file_name = category_list['file-name']
                        variables = category_list['variables']
                        output = category_list['output']
                        component_call_buffer[question_component] = {
                            'instruction statement': get_Component_Template(question_component, file_name, prompt_details['exam'], prompt_details['section'], prompt_details['question-type'], variables, rand_var=rand_var),
                            'output': output,
                            'file-name': file_name,
                            'option-type': prompt_details['option']
                        }
                        # option category is matching
            else:
                # Handling all the other types of questions.
                # because in this case we will go in recursion for managing components
                if component_instruction.get(question_component, None) is None:
                    raise ValueError(
                        f"the component instruction {prettify(question_component, 'Magenta')} is not present in \n{prettify('question_component_types.json', 'Cyan')}")
                component_call_buffer[question_component] = {}
                for component_instruction_option in component_instruction[question_component]:
                    if component_instruction_option.get('QuestionType') is None:
                        raise ValueError(
                            f"Got no QuestionType for: {prettify(question_component, 'Yellow')} -> {prettify(component_instruction_option, 'Magenta')}")
                    if question_type in component_instruction_option['QuestionType']:
                        file_name = component_instruction_option['file-name']
                        variables = component_instruction_option['variables']
                        if component_call_buffer[question_component] != {}:
                            raise ValueError(
                                f"Already there is a value in the case when question_component is {prettify(question_component, 'Yellow')}, for component_call_buffer: {prettify(component_call_buffer, 'Red')}")

                        component_call_buffer[question_component] = {
                            'instruction statement': get_Component_Template(question_component, file_name, prompt_details['exam'], prompt_details['section'], prompt_details['question-type'], variables, rand_var=rand_var),
                            'output': component_instruction_option['output'],
                            'file-name': file_name
                        }
                if component_call_buffer[question_component] == {}:
                    raise ValueError(
                        f"the value of component_call_buffer for {prettify(question_component, 'Red')} is not present for {prettify(question_type, 'Yellow')}")
            component_calls.append(component_call_buffer)
        # endregion

        record(component_calls, 'component_calls',
               prompt_details['question-type'])

        # Generate actual question components using Gemini API BEFORE child recursion
        # Use the pre-initialized self.gemini_generator from generate() method
        if not hasattr(self, 'gemini_generator') or self.gemini_generator is None:
            raise RuntimeError(
                "Gemini generator not initialized. Call from generate() method.")

        # Initialize result buffer to merge components by type
        result_buffer = {}
        calls_generation = []  # Keep for logging purposes

        # Process each component call and generate using Gemini
        # ---- 1️⃣  Build a flat list of every individual call -----------------
        flat_calls = []
        for cc in component_calls:
            for comp_type, data in cc.items():
                if isinstance(data, list):
                    flat_calls.extend([(comp_type, d) for d in data])
                else:
                    flat_calls.append((comp_type, data))
                # Record the generated components before child recursion (for logging)
                record(calls_generation, 'calls_generation',
                       prompt_details['question-type'])

        # ---- 2️⃣  Generate & merge every single call into result_buffer ------
        for comp_type, call in flat_calls:
            context = {
                'component_type': comp_type,
                'question_type': question_type,
                'exam': prompt_details['exam'],
                'section': prompt_details['section'],
                'original_prompt': prompt_details['prompt']
            }
            try:
                generated = self.gemini_generator.generate_component(
                    instruction_statement=call['instruction statement'],
                    expected_output=call['output'],
                    context=context
                )
            except Exception as e:
                generated = {"error": str(e)}

            manage_generated_content(
                result_buffer, question_type, comp_type, generated,
                option_type=prompt_details.get('option')
            )

        # Record the merged result buffer

        # Handle child recursion AFTER component generation and recording
        if prompt_details.get('type') == 'parent':
            # here the complete child prompt data is about to come.
            def _child_add(child_prompt):
                child_prompt_details = {
                    'type': 'child',
                    'exam': prompt_details['exam'],
                    'section': prompt_details['section'],
                    'question-type': prompt_details['question-type'],
                    'option': child_prompt['option'],
                    'prompt': child_prompt['prompt']
                }
                return child_prompt_details

            child_prompt_data = []
            for child_prompt in prompt_details.get('child-prompt'):
                child_prompt = _child_add(child_prompt)
                child_data = self.get_question_data(child_prompt)
                child_prompt_data.append(child_data)
            # child_prompt_data = [self.get_question_data(
            #     _child_add(child_prompt)) for child_prompt in prompt_details.get('child-prompt')]
            result_buffer['child-questions'] = child_prompt_data
        if prompt_details['type'] != 'child':
            record(result_buffer, 'result_buffer',
                   prompt_details['question-type'])
        return result_buffer

    def generate(self) -> dict:
        for exam, sections in self.prompts_dictionary.items():
            paper = {}
            for _, section_data in sections.items():
                section = section_data['section']
                paper[_] = {
                    'section': section,
                    'questions': []
                }
                for qt, qt_info in section_data.items():
                    if qt == 'section':
                        continue
                    # here we need to use threading, inside this function, like every question complete generation task will be given to a separate thread
                    test = ['Problem Solving Simple', 'Problem Solving Meta', 'Data Sufficiency',
                            'Reading Comprehension', 'Text Completion', 'Sentence Equivalence']
                    if qt == test[1]:

                        for i, prompt_data in enumerate(qt_info['prompts']):
                            # Assign API key index cyclically to distribute load
                            api_key_index = 0
                            prompt_details = {
                                'type': qt_info['type'],
                                'exam': exam,
                                'section': section,
                                'question-type': qt,
                                'option': prompt_data.get('option'),
                                'prompt': prompt_data.get('prompt'),
                                'child-prompt': prompt_data.get('child-prompt')
                            }

                            gemini_generator = get_gemini_generator(
                                api_key_index=api_key_index, question_type=qt)
                            self.gemini_generator = gemini_generator
                            question_data = self.get_question_data(
                                prompt_details)
                            paper[_]['questions'].append(question_data)
                        break
