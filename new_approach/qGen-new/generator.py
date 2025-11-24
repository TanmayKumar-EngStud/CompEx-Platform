"""
Here we will get complete prompt dictionary, we will traverse from every question prompt, generate their respective question components as per given in `question_component_types.json`.
"""

import os
import json
from io_utils import get_json, prettify, get_Component_Template, record, append_record
from api_utils import get_gemini_generator
import re
# import concurrent.futures
from typing import Optional
from content_generation_manager import manage_generated_content

all_question_structure = get_json('question_component_types')[0]


def log_generation_stage(exam: str,
                         section: Optional[str] = None,
                         detail: Optional[str] = None) -> None:
    """Print the current generation progress using prettify for readability."""
    segments = [
        f"{prettify('Exam', 'Cyan')}: {prettify(exam, 'Green')}"
    ]
    if section:
        segments.append(
            f"{prettify('Section', 'Cyan')}: {prettify(section, 'Yellow')}"
        )
    if detail:
        segments.append(detail)
    print(f"{prettify('Status', 'Blue')}: " + " | ".join(segments))


class GenQ:
    def __init__(self,
                 prompts_dictionary: dict,
                 target_question_type: Optional[str] = None,
                 max_questions: int = 1) -> None:
        self.prompts_dictionary = prompts_dictionary
        self.target_question_type = target_question_type
        self.max_questions = max_questions
        self.generated_count = 0
        self._log_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'log_json_files',
            'selected_questions'
        )

    def get_templates(self, question_components, prompt_details, component_instruction):
        """
            get the templates for all the question components of given question type 
            and returns a list of component calls for that question prompt

            Args:
                question_components: 
        """
        rand_var = self.rand_var
        prefix = self.prefix
        question_type = self.question_type
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
                            f"The current questionType: {prettify(prompt_details['question-type'], 'Yellow')} is not having the `{prettify('option', 'Red')}` provided with prompt, for question_component: {prettify(prefix+question_component, 'Red', True)} here are the prompt details:\n{prettify(str(prompt_details), 'Blue')}")
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
                            f"Got no QuestionType for: {prettify(question_component, 'Yellow')} -> {prettify(str(component_instruction_option), 'Magenta')}")
                    if question_type in component_instruction_option['QuestionType']:
                        file_name = component_instruction_option['file-name']
                        variables = component_instruction_option['variables']
                        if component_call_buffer[question_component] != {}:
                            raise ValueError(
                                f"Already there is a value in the case when question_component is {prettify(question_component, 'Yellow')}, for component_call_buffer: {prettify(str(component_call_buffer), 'Red')}")

                        component_call_buffer[question_component] = {
                            'instruction statement': get_Component_Template(question_component, file_name, prompt_details['exam'], prompt_details['section'], prompt_details['question-type'], variables, rand_var=rand_var),
                            'output': component_instruction_option['output'],
                            'file-name': file_name
                        }
                if component_call_buffer[question_component] == {}:
                    raise ValueError(
                        f"the value of component_call_buffer for {prettify(question_component, 'Red')} is not present for {prettify(question_type, 'Yellow')}")
            component_calls.append(component_call_buffer)
        return component_calls

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
        self.rand_var = None  # sets how many blanks for text completion

        # --- Dynamic Difficulty Injection ---
        try:
            difficulty_levels = get_json('difficulty_levels')[0]
            
            # Determine Domain
            qt = prompt_details['question-type']
            if qt in ["Data Sufficiency", "Problem Solving Simple", "Problem Solving Meta", "Numerical Entry"]:
                domain = "Quants"
            elif qt in ["Sentence Equivalence", "Text Completion", "Reading Comprehension"]:
                domain = "Verbal"
            else:
                domain = None

            # Extract Difficulty Level
            # Regex to find "difficulty_level:<N>" or "difficulty_level: <N>"
            match = re.search(r'difficulty_level:\s*<(\d)>', prompt_details['prompt'])
            if domain and match:
                level = match.group(1)
                instruction = difficulty_levels.get(domain, {}).get(level)
                
                if instruction:
                    # Append instruction to the prompt
                    prompt_details['prompt'] += f"\n\n[Difficulty Instruction]: {instruction}"

        except Exception as e:
            print(f"Warning: Failed to inject difficulty instruction: {e}")
        # ------------------------------------

        if prompt_details['question-type'] == 'Text Completion':
            self.rand_var = prompt_details['prompt'].split(
                ' - ', 1)[0].strip('<>')

        component_instruction = all_question_structure[1]
        question_components = list(
            all_question_structure[0][prompt_details['type']])
        self.question_type = prompt_details['question-type']
        if not prompt_details.get('metadata-type', None):
            if 'QuestionMetadata' in question_components:
                question_components.remove('QuestionMetadata')
        # if prompt_details.get('type') is None:
        #     # only child prompts are not having 'type'
        #     prompt_details['type'] = 'child'
        self.prefix = '' if prompt_details['type'] == 'simple' else prompt_details['type']

        component_calls = self.get_templates(
            question_components, prompt_details, component_instruction)

        # Generate actual question components using Gemini API BEFORE child recursion
        # Use the pre-initialized self.gemini_generator from generate() method
        if not hasattr(self, 'gemini_generator') or self.gemini_generator is None:
            raise RuntimeError(
                "Gemini generator not initialized. Call from generate() method.")

        # Initialize result buffer to merge components by type
        result_buffer = {}

        # Process each component call and generate using Gemini
        # ---- 1️⃣  Build a flat list of every individual call -----------------
        flat_calls = []
        for cc in component_calls:
            for comp_type, data in cc.items():
                if isinstance(data, list):
                    for entry in data:
                        flat_calls.append((comp_type, entry))
                else:
                    flat_calls.append((comp_type, data))

        # ---- 2️⃣  Generate & merge every single call into result_buffer ------
        for comp_type, call in flat_calls:
            print(
                f"   ↳ Generating {prettify(comp_type, 'Yellow')} for {prettify(self.question_type, 'Magenta')}")
            context = {
                'component_type': comp_type,
                'question_type': self.question_type,
                'exam': prompt_details['exam'],
                'section': prompt_details['section'],
                'original_prompt': prompt_details['prompt'],
                'prompt_type': prompt_details['type'],
                'metadata_blueprint': prompt_details.get('metadata-type'),
                'metadata_content': result_buffer.get(
                    'metadata') or prompt_details.get('metadata'),
                'child_prompt': bool(prompt_details.get('child-prompt'))
            }
            try:
                generated = self.gemini_generator.generate_component(
                    instruction_statement=call['instruction statement'],
                    expected_output=call['output'],
                    context=context
                )
                if isinstance(generated, (dict, list)):
                    preview = json.dumps(generated, ensure_ascii=False)
                else:
                    preview = str(generated)
                snippet = (preview[:200] + '...') if len(preview) > 200 else preview
                print(
                    f"      {prettify(comp_type, 'Green')}: {snippet}")
            except Exception as e:
                generated = {"error": str(e)}
                print(
                    f"      {prettify(comp_type, 'Red')}: {prettify(str(e), 'Yellow')}")

            manage_generated_content(
                result_buffer, self.question_type, comp_type, generated,
                option_type=prompt_details.get('option')
            )

        # Record the merged result buffer

        # Handle child recursion AFTER component generation and recording
        if prompt_details.get('type') == 'parent':
            # here the complete child prompt data is about to come.
            parent_metadata = result_buffer.get('metadata')

            def _child_add(child_prompt):
                child_prompt_details = {
                    'type': 'child',
                    'exam': prompt_details['exam'],
                    'section': prompt_details['section'],
                    'question-type': prompt_details['question-type'],
                    'option': child_prompt['option'],
                    'prompt': child_prompt['prompt'],
                    'metadata': parent_metadata
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
        
        # Log the complete question data (Overwrite mode)
        # safe_name = re.sub(r'[^a-zA-Z0-9]+', '-', prompt_details['prompt'][:50]).strip('-')
        
        # Add prompt to result buffer for logging
        result_buffer['prompt'] = prompt_details['prompt']
        
        record(result_buffer, fname="generated_question", addresses=[self.question_type])
        
        # append_record(result_buffer, fname=self.question_type, addresses=['get_question_data'])
        
        self._persist_selected_question(
            prompt_details['question-type'], result_buffer)
        return result_buffer

    def _persist_selected_question(self, question_type: str, payload: dict) -> None:
        if not self.target_question_type or question_type != self.target_question_type:
            return
        os.makedirs(self._log_base, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9]+', '-',
                           question_type).strip('-') or 'question'
        path = os.path.join(self._log_base, f'{safe_name}.json')
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def generate(self) -> dict:
        paper_set = {}
        for exam, sections in self.prompts_dictionary.items():
            log_generation_stage(
                exam, detail=prettify(
                    'Initializing question generation', 'Magenta')
            )
            paper = {}
            for section_id, section_data in sections.items():
                section = section_data['section']
                log_generation_stage(
                    exam,
                    section,
                    detail=prettify('Generating section content', 'Blue')
                )
                paper[section_id] = {
                    'section': section,
                    'questions': []
                }
                for qt, qt_info in section_data.items():
                    if qt == 'section':
                        continue
                    # here we need to use threading, inside this function, like every question complete generation task will be given to a separate thread
                    # test = ['Problem Solving Simple', 'Problem Solving Meta', 'Data Sufficiency',
                    #         'Reading Comprehension', 'Text Completion', 'Sentence Equivalence']
                    
                    # Allow all configured question types to proceed
                    if True: 
                        log_generation_stage(
                            exam,
                            section,
                            detail=f"{prettify('Question type', 'Cyan')}: {prettify(qt, 'Magenta')}"
                        )

                        for prompt_data in qt_info['prompts']:
                            # Assign API key index cyclically to distribute load
                            api_key_index = 0
                            prompt_details = {
                                'type': qt_info['type'],
                                'exam': exam,
                                'section': section,
                                'question-type': qt,
                                'option': prompt_data.get('option'),
                                'prompt': prompt_data.get('prompt'),
                                'child-prompt': prompt_data.get('child-prompt'),
                                'metadata-type': prompt_data.get('metadata-type')
                            }

                            gemini_generator = get_gemini_generator(
                                api_key_index=api_key_index, question_type=qt)
                            self.gemini_generator = gemini_generator
                            question_data = self.get_question_data(
                                prompt_details)
                            paper[section_id]['questions'].append(
                                question_data)
                            if self.target_question_type and qt == self.target_question_type:
                                self.generated_count += 1
                                print(
                                    f"{prettify('Captured', 'Green')}: {self.generated_count} {qt} question(s)")
                                if self.generated_count >= self.max_questions:
                                    paper_set[exam] = paper
                                    return paper_set
                        break
            paper_set[exam] = paper
        return paper_set
