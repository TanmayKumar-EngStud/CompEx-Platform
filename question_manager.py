
import os
import random
import json
import re
from typing import Optional, List, Dict, Any, Tuple

from io_utils import get_json, prettify, get_Component_Template, record, get_Question_Template
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

                # Special handling for blank options to select correct template (single vs multi)
                if self.prompt_details['option'] == 'blank':
                    # Determine number of blanks from variables or context
                    # variables is usually None for options in config, but we need to check prompt_details or similar
                    # Actually, for Text Completion, the number of blanks is usually in the question type or determined elsewhere.
                    # But here we need to pick the template.
                    # Let's check prompt_details['question-type'] or variables if available.
                    # Wait, variables is passed to get_Component_Template.
                    # In config, variables is null for options.
                    # We need a way to know if it's TC-1, TC-2, TC-3.
                    # This information might be in self.prompt_details['variables'] if it exists?
                    # Let's assume we can infer it or use a default.
                    # Actually, the template had {{#if_TC-1}}, which implies the variable is passed to the template.
                    # We can check self.rand_var or variables passed to get_Component_Template.
                    # But get_Component_Template is called *after* this selection.
                    
                    # Workaround: Check if 'TC-1' is in self.rand_var (if available) or just default to multi if unsure?
                    # Or better, check the question type subtype if available.
                    # For now, let's try to detect it from self.rand_var if possible.
                    is_single_blank = False
                    if self.rand_var and 'TC-1' in self.rand_var:
                         is_single_blank = True
                    
                    if is_single_blank:
                        file_name = 'blank-single-question-option-answer.txt.template'
                    else:
                        file_name = 'blank-multi-question-option-answer.txt.template'

                return {
                    'instruction statement': get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, rand_var=self.rand_var),
                    'output': output,
                    'file-name': file_name,
                    'option-type': self.prompt_details['option']
                }
        raise ValueError(f"No matching option instruction found for component '{component_name}', option type '{self.prompt_details['option']}', question type '{self.prompt_details['question-type']}'")

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
    Injects difficulty, orchestrates templates, calls Deepseek Session, and handles persistence.
    """
    def __init__(self, 
                 prompt_details: dict, 
                 generator_session, # Replaced gemini_generator
                 target_question_type: Optional[str] = None):
        self.prompt_details = prompt_details
        self.generator_session = generator_session
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
        
        # 1b. Inject Context (Vocab + Scenarios)
        self._inject_context_and_vocab()

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

        # 4. Generate Content via Deepseek Session
        # First, ensure system instruction is set if not already
        if hasattr(self.generator_session, 'set_system_instruction'):
             # We can load the system instruction from api_utils logic or just use a default one valid for the session
             # The session manages it. But ideally we pass it.
             # For now, let's assume the session or the generator method handles "SystemInstruction" concept if we were using Gemini.
             # With Deepseek, we set it once.
             # Let's extract the system instruction using helper or just set a generic one.
             # Actually, api_utils had `_load_system_instructions`. We can replicate that or import it.
             # But simplicity: "You are an expert exam question generator."
             # Or better: call internal method to load it.
             pass 

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
        
        # Inject DB-required fields
        try:
             # Parse difficulty from prompt details or fallback
             if 'difficulty' in self.prompt_details:
                 result_buffer['difficulty'] = self.prompt_details['difficulty']
             elif 'difficulty' not in result_buffer:
                 # Attempt to extract from 'difficulty_level: <N>' in nomenclature if available
                 import re
                 match = re.search(r'difficulty_level:\s*(\d+)', self.prompt_details.get('prompt', ''))
                 if match:
                     result_buffer['difficulty'] = int(match.group(1))
                 else:
                     result_buffer['difficulty'] = 1 # Default
        except:
             result_buffer['difficulty'] = 1

        # Tags
        # Tags Parsing Logic
        tags = []
        def clean_tag(tag_str: str) -> str:
            """Removes < and > from tag strings"""
            return tag_str.replace('<', '').replace('>', '')

        try:
            prompt_parts = self.prompt_details['prompt'].split(' - ')
            
            # Always add type
            tags.append(clean_tag(f"type: {self.question_type}"))

            # Topic and Theme Extraction
            if self.question_type == 'Sentence Equivalence':
                # Format: <Theme> - <Skill>
                if len(prompt_parts) > 0:
                    tags.append(clean_tag(f"theme: {prompt_parts[0]}"))
                if len(prompt_parts) > 1:
                    tags.append(clean_tag(f"topic: {prompt_parts[1]}")) # User requested mapping skill to topic
            
            elif self.question_type in ['Text Completion', 'Reading Comprehension']:
                # Format: <Type> - <Theme> - <Skill>
                if len(prompt_parts) > 1:
                    tags.append(clean_tag(f"theme: {prompt_parts[1]}"))
                if len(prompt_parts) > 2:
                    tags.append(clean_tag(f"topic: {prompt_parts[2]}")) # User requested mapping skill to topic
            
            else:
                # Quants & Integrated Reasoning
                # Format: <Topic> - <Theme>
                if len(prompt_parts) > 0:
                    tags.append(clean_tag(f"topic: {prompt_parts[0]}"))
                if len(prompt_parts) > 1:
                    tags.append(clean_tag(f"theme: {prompt_parts[1]}"))

            # Removed Exam/Section tags as per request
            
        except Exception as e:
            print(f"Warning: Tag parsing failed: {e}")
            tags.append(f"type: {self.question_type}") # Fallback

        # CRITICAL FIX: Assign tags to result_buffer before recording!
        result_buffer['tags'] = list(set(tags))

        return result_buffer, stats
        
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

    def _inject_context_and_vocab(self):
        """
        Injects Vocabulary and Scenario Context into the prompt *before* generation.
        """
        # --- VOCABULARY INJECTION ---
        if self.question_type in ['Text Completion', 'Reading Comprehension', 'Sentence Equivalence', 'Critical Reasoning', 'Sentence Correction']:
            try:
                vocab_path = os.path.join(os.path.dirname(__file__), 'json_files', 'vocabulary.json')
                if os.path.exists(vocab_path):
                    with open(vocab_path, 'r') as f:
                        vocab_data = json.load(f)

                    exam = self.prompt_details.get('exam', 'GRE')
                    if exam not in vocab_data: exam = 'GRE'
                    
                    current_difficulty = self.prompt_details.get('difficulty', 1)
                    diff_key = str(max(1, min(5, current_difficulty)))
                    
                    word_list = vocab_data.get(exam, {}).get(diff_key, [])
                    
                    if word_list:
                        count = 15 if self.question_type in ['Reading Comprehension', 'Critical Reasoning'] else 10
                        selected_words = random.sample(word_list, min(len(word_list), count))
                        
                        vocab_instruction = f"\n\n[Vocabulary Instruction]: Integrate the following words naturally into the text (or options where appropriate): {', '.join(selected_words)}."
                        self.prompt_details['prompt'] += vocab_instruction
            except Exception as e:
                print(f"Warning: Failed to inject vocabulary: {e}")

        # --- SCENARIO INJECTION ---
        try:
            scenario_path = os.path.join(os.path.dirname(__file__), 'json_files', 'scenarios.json')
            if os.path.exists(scenario_path):
                with open(scenario_path, 'r') as f:
                    scenarios_data = json.load(f)
                
                random_scenario = random.choice(scenarios_data['scenarios'])
                scenario_instruction = f"\n\n[Scenario Context]: Set this problem in the context of {random_scenario}."
                uniqueness_seed = f" Random Seed: {random.randint(10000, 99999)}"
                
                self.prompt_details['prompt'] += scenario_instruction + uniqueness_seed
        except Exception as e:
            print(f"Warning: Failed to inject scenario: {e}")

    def _generate_components(self, component_calls: list) -> Tuple[dict, dict]:
        result_buffer = {}
        total_stats = {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
        
        if not self.generator_session.system_instructions_set:
             try:
                 # Determine template name based on Question Type mapping
                 q_type = self.question_type
                 template_map = {
                     "Data Sufficiency": "data-sufficiency-system-instruction.txt.template",
                     "Problem Solving Simple": "problem-solving-simple-system-instruction.txt.template",
                     "Problem Solving Meta": "problem-solving-meta-system-instruction.txt.template",
                     "Numerical Entry": "numerical-entry-system-instruction.txt.template",
                     "Quantitative Comparison": "qc-system-instruction.txt.template",
                     "Text Completion": "text-completion-system-instruction.txt.template",
                     "Reading Comprehension": "reading-comprehension-system-instruction.txt.template",
                     "Sentence Equivalence": "sentence-equivalence-system-instruction.txt.template",
                     "Graphic Interpretation": "gi-system-instruction.txt.template",
                     "Table Analysis": "ta-system-instruction.txt.template",
                     "Two-Part Analysis": "tpa-system-instruction.txt.template",
                     "Multi-Source Reasoning": "msr-system-instruction.txt.template"
                 }
                 # Default to generic if not found (e.g. Critical Reasoning, Sentence Correction)
                 template_name = template_map.get(q_type, "generic.txt.template")
                 
                 if template_name:
                     sys_instruct = get_Question_Template(
                        question_component="SystemInstruction",
                        filename=template_name,
                        exam_type=self.prompt_details['exam'],
                        Section_name=self.prompt_details['section'],
                        question_type=self.question_type,
                        variable=None
                     )
                     self.generator_session.set_system_instruction(sys_instruct.strip())
             except Exception as e:
                 print(f"Warning: Failed to load system instruction: {e}")

        # Flatten calls for processing
        flat_calls = []
        for cc in component_calls:
            for comp_type, data in cc.items():
                if isinstance(data, list):
                    for entry in data:
                        flat_calls.append((comp_type, entry))
                else:
                    flat_calls.append((comp_type, data))

        generated_question_text = None

        for comp_type, call in flat_calls:
            # print(f"   ↳ Generating {prettify(comp_type, 'Yellow')} for {prettify(self.question_type, 'Magenta')}")
            
            context = {
                'component_type': comp_type,
                'question_type': self.question_type,
                'template_filename': call.get('file-name'),
                'exam': self.prompt_details['exam'],
                'section': self.prompt_details['section'],
                'original_prompt': self.prompt_details['prompt'],
                'prompt_type': self.prompt_details['type'],
                'metadata_blueprint': self.prompt_details.get('metadata-type'),
                'metadata_content': result_buffer.get('metadata') or self.prompt_details.get('metadata'),
                'child_prompt': bool(self.prompt_details.get('child-prompt')),
                'generated_question': generated_question_text  # Inject previously generated question
            }

            try:
                # Use session for generation (it maintains history)
                generated, stats = self.generator_session.generate_component(
                    instruction_statement=call['instruction statement'],
                    expected_output=call['output'],
                    context=context
                )
                
                # Capture the generated question text if this component is the Question Text
                if comp_type == 'QuestionText':
                    if isinstance(generated, dict):
                        # Try to find the text content in common keys
                        generated_question_text = generated.get('question') or generated.get('question_text') or str(generated)
                    else:
                        generated_question_text = str(generated)

                # Accumulate stats
                total_stats['input_tokens'] += stats['input_tokens']
                total_stats['output_tokens'] += stats['output_tokens']
                total_stats['api_calls'] += 1
                
                # # Preview logging
                # preview = json.dumps(generated, ensure_ascii=False) if isinstance(generated, (dict, list)) else str(generated)
                # snippet = (preview[:200] + '...') if len(preview) > 200 else preview
                # print(f"      {prettify(comp_type, 'Green')}: {snippet}")

            except Exception as e:
                # CRITICAL: Re-raise "Request Per Day" errors so thread_creator can blacklist the key
                if "Request Per Day limit exceeded" in str(e):
                    raise e

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
                # Ideally, we SHARE the session so the child knows the parent Context?
                # YES. "Multi rounded conversation". The child is part of the same flow usually.
                # If child questions are part of the same "Conversation" (e.g. Reading Comp), share session.
                # If they are independent items just grouped, maybe new session?
                # User said: "Multi rounded conversation ... for every question(simple and parent) ... on different thread".
                # This implies one thread/session per Top Level Question.
                # So child questions should share the session.
                
                child_manager = ManageQuestionData(
                    prompt_details=child_prompt_details,
                    generator_session=self.generator_session, # Share session
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


