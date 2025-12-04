import os
import json
import re
from typing import Optional, List, Dict, Any, Tuple

from io_utils import get_json, prettify, get_Component_Template, record
from api_utils import get_gemini_generator
from content_generation_manager import manage_generated_content

all_question_structure = get_json('question_component_types')[0]

class ManageComponentTemplates:
    """
    Responsible solely for generating the instruction templates and output structures
    for specific question components.
    """
    def __init__(self, 
                 question_components: list, 
                 prompt_details: dict, 
                 component_instruction: dict,
                 rand_var: Any = None):
        
        self.question_components = question_components
        self.prompt_details = prompt_details
        self.component_instruction = component_instruction
        self.rand_var = rand_var
        self.question_type = prompt_details['question-type']
        self.prefix = '' if prompt_details['type'] == 'simple' else prompt_details['type']
        
        # This list will hold the final result
        self.templates = []
        
        # Trigger generation immediately
        self._generate_all_templates()

    def _generate_all_templates(self):
        """Iterates through components and routes to specific internal handlers."""
        for question_component in self.question_components:
            component_call_buffer = {}

            if question_component == 'ChildQuestions':
                continue
            
            elif question_component == "QuestionMetadata":
                component_call_buffer[question_component] = self._handle_metadata(question_component)
                
            elif question_component == "QuestionOptions/Answer":
                component_call_buffer[question_component] = self._handle_options(question_component)
                
            else:
                # Standard Generic Components
                component_call_buffer[question_component] = self._handle_generic_component(question_component)

            if component_call_buffer:
                self.templates.append(component_call_buffer)

    def _handle_metadata(self, component_name: str) -> List[Dict]:
        """Handles logic for QuestionMetadata, including MSR and standard passages."""
        buffer = []
        prompt_metadata_types = list(self.prompt_details['metadata-type'].keys())
        
        for prompt_metadata_type in prompt_metadata_types:
            if prompt_metadata_type == 'passage':
                # Standard Passage Logic
                for prompt_metadata_item in self.prompt_details['metadata-type'][prompt_metadata_type]:
                    count_number_of_passages = len(self.prompt_details.get('child-prompt', 1))
                    file_name = self.component_instruction[component_name][prompt_metadata_type]['file-name']
                    variables = self.component_instruction[component_name][prompt_metadata_type]['variables']
                    
                    for para_no in range(1, count_number_of_passages+1):
                        buffer.append({
                            "instruction statement": f"Generate para {para_no} of {count_number_of_passages}:\n{get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var=self.rand_var)}",
                            "output": self.component_instruction[component_name][prompt_metadata_type]['output']
                        })
            else:
                # Special handling for Multi-Source Reasoning (MSR)
                if self.question_type == 'Multi-Source Reasoning':
                    buffer.extend(self._handle_msr_metadata(component_name, prompt_metadata_type))
                else:
                    # Standard non-MSR metadata (Tables, Charts, etc.)
                    for prompt_metadata_item in self.prompt_details['metadata-type'][prompt_metadata_type]:
                        file_name = self.component_instruction[component_name][prompt_metadata_type]['file-name']
                        variables = self.component_instruction[component_name][prompt_metadata_type]['variables']
                        buffer.append({
                            "instruction statement": get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var=self.rand_var),
                            "output": self.component_instruction[component_name][prompt_metadata_type]['output'],
                            'file-name': file_name
                        })
        return buffer

    def _handle_msr_metadata(self, component_name: str, prompt_metadata_type: str) -> List[Dict]:
        """Specific logic for extracting MSR sources and skills."""
        buffer = []
        prompt_text = self.prompt_details.get('prompt', '')
        parts = prompt_text.split(' - ')
        
        source_types = []
        focused_skills = []
        source_keywords = ['passage', 'table', 'graph', 'chart', 'email', 'memo']
        
        # Parsing Logic
        for part in parts:
            clean_part = part.strip().lower()
            if clean_part in source_keywords and len(source_types) < 3:
                source_types.append(clean_part)
        
        for i, part in enumerate(parts):
            if i > 1 and 'difficulty' not in part.lower():
                clean_part = part.strip()
                if clean_part.lower() not in source_keywords and clean_part and len(focused_skills) < 3:
                    focused_skills.append(clean_part)
        
        # Fallbacks
        if len(source_types) < 3:
            source_types = ['passage', 'table', 'graph'][:3]
        if len(focused_skills) < 3:
            focused_skills = ['Data Interpretation', 'Trend Analysis', 'Comparison and Contrast'][:3]

        for source_num in range(1, 4):
            source_type = source_types[source_num - 1]
            focused_skill = focused_skills[source_num - 1]
            
            # Determine Types
            if source_type in ['passage', 'email', 'memo']:
                metadata_item = 'passage'
                meta_type = 'passage'
            elif source_type in ['table']:
                meta_type = prompt_metadata_type
                metadata_item = self.prompt_details['metadata-type'][prompt_metadata_type][0] if self.prompt_details['metadata-type'][prompt_metadata_type] else 'data_table'
            elif source_type in ['graph', 'chart']:
                meta_type = prompt_metadata_type
                metadata_item = self.prompt_details['metadata-type'][prompt_metadata_type][0] if self.prompt_details['metadata-type'][prompt_metadata_type] else 'line_chart'
            else:
                meta_type = prompt_metadata_type
                metadata_item = self.prompt_details['metadata-type'][prompt_metadata_type][0]

            file_name = self.component_instruction[component_name][meta_type]['file-name']
            variables = self.component_instruction[component_name][meta_type]['variables']
            
            base_template = get_Component_Template(
                component_name, file_name, 
                self.prompt_details['exam'], self.prompt_details['section'], 
                self.prompt_details['question-type'], variables, 
                meta_type, metadata_item, 
                rand_var=self.rand_var
            )
            
            theme = parts[1] if len(parts) > 1 else 'Business scenario'
            
            msr_template_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'json_files', 'component_templates', 'QuestionMetadata', 'msr_source_instructions.json'
            )
            with open(msr_template_path, 'r', encoding='utf-8') as f:
                msr_config = json.load(f)
            
            instruction_with_context = msr_config['instruction_template'].format(
                source_num=source_num, source_type=source_type,
                focused_skill=focused_skill, theme=theme,
                base_template=base_template
            )
            
            buffer.append({
                "instruction statement": instruction_with_context,
                "output": self.component_instruction[component_name][meta_type]['output'],
                'file-name': file_name,
                'source_number': source_num,
                'source_type': source_type,
                'focused_skill': focused_skill
            })
        return buffer

    def _handle_options(self, component_name: str) -> Dict:
        """Handles QuestionOptions/Answer logic."""
        for category_list in self.component_instruction.get(component_name):
            if category_list.get('type', None) is None:
                raise ValueError(f"{prettify(component_name, 'Yellow')} missing type")
            
            if self.prompt_details.get('option', None) is None:
                raise ValueError(f"Option type missing in prompt details for {component_name}")

            if (self.prompt_details['option'] == category_list['type'] and 
                self.prompt_details['question-type'] in category_list['QuestionType']):
                
                file_name = category_list['file-name']
                variables = category_list['variables']
                output = category_list['output']
                return {
                    'instruction statement': get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, rand_var=self.rand_var),
                    'output': output,
                    'file-name': file_name,
                    'option-type': self.prompt_details['option']
                }
        return {}

    def _handle_generic_component(self, component_name: str) -> Dict:
        """Handles other components via recursion through instruction list."""
        if self.component_instruction.get(component_name, None) is None:
            raise ValueError(f"Component instruction {prettify(component_name, 'Magenta')} not found.")
        
        result = {}
        for component_instruction_option in self.component_instruction[component_name]:
            if component_instruction_option.get('QuestionType') is None:
                raise ValueError(f"No QuestionType for {component_name}")
            
            if self.question_type in component_instruction_option['QuestionType']:
                if result:
                    raise ValueError(f"Multiple instruction matches for {component_name}")

                file_name = component_instruction_option['file-name']
                variables = component_instruction_option['variables']
                
                result = {
                    'instruction statement': get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, rand_var=self.rand_var),
                    'output': component_instruction_option['output'],
                    'file-name': file_name
                }
        
        if not result:
            raise ValueError(f"No instruction found for {component_name} in {self.question_type}")
        return result


class ManageQuestionData:
    """
    Manages the lifecycle of generating a single question (and its children).
    Injects difficulty, orchestrates templates, calls Gemini, and handles persistence.
    """
    def __init__(self, 
                 prompt_details: dict, 
                 gemini_generator, 
                 target_question_type: Optional[str] = None):
        self.prompt_details = prompt_details
        self.gemini_generator = gemini_generator
        self.target_question_type = target_question_type
        self.question_type = prompt_details['question-type']
        self._log_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'log_json_files',
            'selected_questions'
        )
        self.rand_var = None

    def get_question_data(self) -> Tuple[dict, dict]:
        """Main entry point to generate data for this question."""
        
        # 1. Dynamic Difficulty Injection
        self._inject_difficulty()

        # 2. Variable initialization
        if self.question_type == 'Text Completion':
            self.rand_var = self.prompt_details['prompt'].split(' - ', 1)[0].strip('<>')
        
        component_instruction = all_question_structure[1]
        question_components = list(all_question_structure[0][self.prompt_details['type']])
        
        if not self.prompt_details.get('metadata-type', None):
            if 'QuestionMetadata' in question_components:
                question_components.remove('QuestionMetadata')

        # 3. Get Templates (Using the new class)
        # The constructor calculates templates immediately
        template_manager = ManageComponentTemplates(
            question_components=question_components,
            prompt_details=self.prompt_details,
            component_instruction=component_instruction,
            rand_var=self.rand_var
        )
        component_calls = template_manager.templates

        # 4. Generate Content via Gemini
        result_buffer, stats = self._generate_components(component_calls)

        # 5. Handle Recursion (Child Questions)
        child_stats = self._handle_child_questions(result_buffer)
        
        # Accumulate child stats
        stats['input_tokens'] += child_stats['input_tokens']
        stats['output_tokens'] += child_stats['output_tokens']
        stats['api_calls'] += child_stats['api_calls']

        # 6. Logging and Recording
        result_buffer['prompt'] = self.prompt_details['prompt']
        result_buffer['question-type'] = self.question_type
        record(result_buffer, fname="generated_question", addresses=[self.question_type])
        self._persist_selected_question(self.question_type, result_buffer)
        
        return result_buffer, stats

    def _inject_difficulty(self):
        try:
            difficulty_levels = get_json('difficulty_levels')[0]
            qt = self.question_type
            
            # Determine Domain
            if qt in ["Data Sufficiency", "Problem Solving Simple", "Problem Solving Meta", "Numerical Entry"]:
                domain = "Quants"
            elif qt in ["Sentence Equivalence", "Text Completion", "Reading Comprehension"]:
                domain = "Verbal"
            elif qt in ["Multi-Source Reasoning", "Two-Part Analysis", "Table Analysis", "Graphic Interpretation"]:
                domain = "Integrated Reasoning"
            else:
                domain = None

            match = re.search(r'difficulty_level:\s*<(\d)>', self.prompt_details['prompt'])
            if domain and match:
                level = match.group(1)
                instruction = difficulty_levels.get(domain, {}).get(level)
                if instruction:
                    self.prompt_details['prompt'] += f"\n\n[Difficulty Instruction]: {instruction}"
        except Exception as e:
            print(f"Warning: Failed to inject difficulty instruction: {e}")

    def _generate_components(self, component_calls: list) -> Tuple[dict, dict]:
        result_buffer = {}
        total_stats = {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
        
        # Ensure generator matches current question type
        if self.gemini_generator.question_type != self.question_type:
            self.gemini_generator = get_gemini_generator(
                api_key_index=self.gemini_generator.api_key_index, 
                question_type=self.question_type
            )

        # Flatten calls for processing
        flat_calls = []
        for cc in component_calls:
            for comp_type, data in cc.items():
                if isinstance(data, list):
                    for entry in data:
                        flat_calls.append((comp_type, entry))
                else:
                    flat_calls.append((comp_type, data))

        for comp_type, call in flat_calls:
            # print(f"   ↳ Generating {prettify(comp_type, 'Yellow')} for {prettify(self.question_type, 'Magenta')}")
            
            context = {
                'component_type': comp_type,
                'question_type': self.question_type,
                'exam': self.prompt_details['exam'],
                'section': self.prompt_details['section'],
                'original_prompt': self.prompt_details['prompt'],
                'prompt_type': self.prompt_details['type'],
                'metadata_blueprint': self.prompt_details.get('metadata-type'),
                'metadata_content': result_buffer.get('metadata') or self.prompt_details.get('metadata'),
                'child_prompt': bool(self.prompt_details.get('child-prompt'))
            }

            try:
                generated, stats = self.gemini_generator.generate_component(
                    instruction_statement=call['instruction statement'],
                    expected_output=call['output'],
                    context=context
                )
                
                # Accumulate stats
                total_stats['input_tokens'] += stats['input_tokens']
                total_stats['output_tokens'] += stats['output_tokens']
                total_stats['api_calls'] += 1
                
                # # Preview logging
                # preview = json.dumps(generated, ensure_ascii=False) if isinstance(generated, (dict, list)) else str(generated)
                # snippet = (preview[:200] + '...') if len(preview) > 200 else preview
                # print(f"      {prettify(comp_type, 'Green')}: {snippet}")

            except Exception as e:
                generated = {"error": str(e)}
                print(f"      {prettify(comp_type, 'Red')}: {prettify(str(e), 'Yellow')}")

            source_info = None
            if comp_type == 'QuestionMetadata' and self.question_type == 'Multi-Source Reasoning':
                source_info = {k: call.get(k) for k in ['source_number', 'source_type', 'focused_skill'] if k in call}
            
            manage_generated_content(
                result_buffer, self.question_type, comp_type, generated,
                option_type=self.prompt_details.get('option'),
                source_info=source_info
            )
        
        return result_buffer, total_stats

    def _handle_child_questions(self, result_buffer: dict) -> dict:
        total_child_stats = {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
        
        if self.prompt_details.get('type') == 'parent':
            parent_metadata = result_buffer.get('metadata')
            child_prompt_data = []
            
            for child_prompt in self.prompt_details.get('child-prompt'):
                child_prompt_details = {
                    'type': 'child',
                    'exam': self.prompt_details['exam'],
                    'section': self.prompt_details['section'],
                    'question-type': child_prompt.get('question-type', self.prompt_details['question-type']),
                    'option': child_prompt['option'],
                    'prompt': child_prompt['prompt'],
                    'metadata': parent_metadata
                }
                # Recursion: Create a new manager for the child
                child_manager = ManageQuestionData(
                    prompt_details=child_prompt_details,
                    gemini_generator=self.gemini_generator,
                    target_question_type=self.target_question_type
                )
                child_data, child_stats = child_manager.get_question_data()
                child_prompt_data.append(child_data)
                
                # Accumulate stats
                total_child_stats['input_tokens'] += child_stats['input_tokens']
                total_child_stats['output_tokens'] += child_stats['output_tokens']
                total_child_stats['api_calls'] += child_stats['api_calls']
                
            result_buffer['child-questions'] = child_prompt_data
            
        return total_child_stats

    def _persist_selected_question(self, question_type: str, payload: dict) -> None:
        if not self.target_question_type or question_type != self.target_question_type:
            return
        os.makedirs(self._log_base, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9]+', '-', question_type).strip('-') or 'question'
        path = os.path.join(self._log_base, f'{safe_name}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
