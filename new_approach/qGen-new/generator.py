"""
Here we will get complete prompt dictionary, we will traverse from every question prompt, generate their respective question components as per given in `question_component_types.json`.
"""

from io_utils import get_json, prettify, get_Component_Template, record
from api_utils import get_gemini_generator
import os
import json
import threading
import concurrent.futures
from typing import Dict, Any, List


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

        # fetching raw templates
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
                        component_call_buffer[prompt_metadata_type] = list()
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
                            'file-name': file_name
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

        # Record component calls first
        record(component_calls, 'component_calls',
               prompt_details['question-type'])

        # Generate actual question components using Gemini API BEFORE child recursion
        # Use the pre-initialized self.gemini_generator from generate() method
        if not hasattr(self, 'gemini_generator') or self.gemini_generator is None:
            raise RuntimeError(
                "Gemini generator not initialized. Call from generate() method.")

        calls_generation = []

        # Process each component call and generate using Gemini
        for component_call in component_calls:
            for component_type, call_data in component_call.items():
                if isinstance(call_data, list):
                    # Multiple calls for this component type (e.g., metadata with multiple items)
                    component_results = []
                    for call in call_data:
                        try:
                            context = {
                                'component_type': component_type,
                                'question_type': prompt_details['question-type'],
                                'exam': prompt_details['exam'],
                                'section': prompt_details['section']
                            }

                            result = self.gemini_generator.generate_component(
                                instruction_statement=call['instruction statement'],
                                expected_output=call['output'],
                                context=context
                            )
                            component_results.append(result)

                        except Exception as e:
                            print(
                                f"❌ Failed to generate {prettify(component_type, 'Red')} component: {str(e)}")
                            # Add error placeholder to maintain structure
                            component_results.append({"error": str(e)})

                    calls_generation.append({
                        "question_component": component_type,
                        "returned_values": component_results
                    })
                else:
                    # Single call for this component type
                    try:
                        context = {
                            'component_type': component_type,
                            'question_type': prompt_details['question-type'],
                            'exam': prompt_details['exam'],
                            'section': prompt_details['section']
                        }

                        result = self.gemini_generator.generate_component(
                            instruction_statement=call_data['instruction statement'],
                            expected_output=call_data['output'],
                            context=context
                        )

                        calls_generation.append({
                            "question_component": component_type,
                            "returned_value": result
                        })

                    except Exception as e:
                        print(
                            f"❌ Failed to generate {prettify(component_type, 'Red')} component: {str(e)}")
                        # Add error placeholder to maintain structure
                        calls_generation.append({
                            "question_component": component_type,
                            "returned_value": {"error": str(e)}
                        })

        # Record the generated components before child recursion
        record(calls_generation, 'calls_generation',
               prompt_details['question-type'])

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

            child_prompt_data = [self.get_question_data(
                _child_add(child_prompt)) for child_prompt in prompt_details.get('child-prompt')]

        return None

    def _process_single_question(self, prompt_data: Dict[str, Any], qt_info: Dict[str, Any],
                                 exam: str, section: str, qt: str, api_key_index: int) -> Dict[str, Any]:
        """
        Process a single question in a separate thread with its own API key index.

        Args:
            prompt_data: Individual prompt data
            qt_info: Question type info
            exam: Exam type (GRE/GMAT)
            section: Section name
            qt: Question type
            api_key_index: API key index for this thread

        Returns:
            Generated question content or error info
        """
        try:
            # Create prompt details for this specific question
            prompt_details = {
                'type': qt_info['type'],
                'exam': exam,
                'section': section,
                'question-type': qt,
                'option': prompt_data.get('option'),
                'prompt': prompt_data.get('prompt')
            }

            if prompt_data.get('child-prompt'):
                prompt_details['child-prompt'] = prompt_data['child-prompt']
                prompt_details['metadata-type'] = prompt_data['metadata-type']

            # Initialize Gemini generator with specific API key index for this thread
            thread_id = threading.current_thread().ident

            # Create a thread-local generator instance
            gemini_generator = get_gemini_generator(
                api_key_index=api_key_index, question_type=qt)

            try:
                # Temporarily assign to self for get_question_data to use
                # Note: This is thread-safe since each thread has its own execution context
                original_generator = getattr(self, 'gemini_generator', None)
                self.gemini_generator = gemini_generator

                question_content = self.get_question_data(prompt_details)

                print(
                    f"✅ Thread {thread_id}: Successfully generated question for {prettify(qt, 'Green')}")
                return {
                    'prompt': prompt_details['prompt'],
                    'question_content': question_content,
                }

            finally:
                # Restore original generator state
                self.gemini_generator = original_generator
                print(
                    f"🧹 Thread {thread_id}: Cleaned up Gemini generator for {prettify(qt, 'Cyan')}")

        except Exception as e:
            thread_id = threading.current_thread().ident
            error_msg = str(e)
            print(
                f"❌ Thread {thread_id}: Failed to generate question for {prettify(qt, 'Red')}: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'prompt_details': prompt_details if 'prompt_details' in locals() else None,
                'api_key_index': api_key_index,
                'thread_id': thread_id
            }

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
                        # Prepare threading for parallel question generation
                        prompts_to_process = qt_info['prompts']
                        # Limit concurrent threads
                        max_workers = min(len(prompts_to_process), 10)

                        print(
                            f"🚀 Starting parallel generation for {len(prompts_to_process)} {prettify(qt, 'Yellow')} questions using {max_workers} threads")

                        # Create thread pool and submit tasks
                        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                            # Submit all question generation tasks
                            future_to_prompt = {}

                            for i, prompt_data in enumerate(prompts_to_process):
                                # Assign API key index cyclically to distribute load
                                api_key_index = i % max_workers

                                future = executor.submit(
                                    self._process_single_question,
                                    prompt_data, qt_info, exam, section, qt, api_key_index
                                )
                                future_to_prompt[future] = {
                                    'prompt_data': prompt_data,
                                    'api_key_index': api_key_index,
                                    'question_index': i
                                }

                            # Collect results as they complete
                            completed_questions = []
                            failed_questions = []

                            for future in concurrent.futures.as_completed(future_to_prompt):
                                prompt_info = future_to_prompt[future]

                                try:
                                    result = future.result()

                                    # Default to True if not specified
                                    if result.get('success', True):
                                        completed_questions.append({
                                            'question_index': prompt_info['question_index'],
                                            'result': result,
                                            'api_key_used': prompt_info['api_key_index']
                                        })
                                        print(
                                            f"✅ Question {prompt_info['question_index'] + 1}/{len(prompts_to_process)} completed")
                                    else:
                                        failed_questions.append({
                                            'question_index': prompt_info['question_index'],
                                            'error': result.get('error', 'Unknown error'),
                                            'api_key_used': prompt_info['api_key_index']
                                        })
                                        print(
                                            f"❌ Question {prompt_info['question_index'] + 1}/{len(prompts_to_process)} failed")

                                except Exception as e:
                                    failed_questions.append({
                                        'question_index': prompt_info['question_index'],
                                        'error': str(e),
                                        'api_key_used': prompt_info['api_key_index']
                                    })
                                    print(
                                        f"❌ Question {prompt_info['question_index'] + 1}/{len(prompts_to_process)} failed with exception: {str(e)}")

                        if failed_questions:
                            print(f"   🔍 Failed question details:")
                            for failure in failed_questions:
                                print(
                                    f"      Question {failure['question_index'] + 1}: {failure['error']}")

                        # Add successful questions to paper (sorted by original index)
                        completed_questions.sort(
                            key=lambda x: x['question_index'])
                        for question_result in completed_questions:
                            paper[_]['questions'].append(
                                question_result['result'])

                        # Only process first question type for now (break after first match)
                        break
                        # print(
                        #     f"{prettify(qt, 'Yellow')} is having this question component\n{prettify(question_content, 'Magenta')}\n")
