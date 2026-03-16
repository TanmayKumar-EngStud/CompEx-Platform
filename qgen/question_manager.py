
import os
import random
import json
import re
from typing import Optional, List, Dict, Any, Tuple

from io_utils import get_json, prettify, get_Component_Template, record, get_Question_Template
from content_generation_manager import manage_generated_content
from db_artilaries import artilaries

all_question_structure = None

async def initialize_question_manager():
    global all_question_structure
    all_question_structure = await artilaries.get_question_component_mapping()

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

    async def generate_all_templates(self):
        """Iterates through components and routes to specific internal handlers."""
        from io_utils import async_get_Component_Template

        for question_component in self.question_components:
            component_call_buffer = {}

            if question_component == 'ChildQuestions':
                continue
            
            elif question_component == "QuestionMetadata":
                component_call_buffer[question_component] = await self._handle_metadata(question_component)
                
            elif question_component == "QuestionOptions/Answer":
                component_call_buffer[question_component] = await self._handle_options(question_component)
                

            else:
                # Standard Generic Components
                component_call_buffer[question_component] = await self._handle_generic_component(question_component)

            if component_call_buffer:
                self.templates.append(component_call_buffer)

    async def _handle_metadata(self, component_name: str) -> List[Dict]:
        """Handles logic for QuestionMetadata, including MSR and standard passages."""
        from io_utils import async_get_Component_Template
        buffer = []
        prompt_metadata_types = list(self.prompt_details['metadata-type'].keys())
        
        for prompt_metadata_type in prompt_metadata_types:
            if prompt_metadata_type == 'passage':
                # Standard Passage Logic
                for prompt_metadata_item in self.prompt_details['metadata-type'][prompt_metadata_type]:
                    child_prompts = self.prompt_details.get('child-prompt')
                    count_number_of_passages = len(child_prompts) if isinstance(child_prompts, list) else 1
                    file_name = self.component_instruction[component_name][prompt_metadata_type]['file-name']
                    variables = self.component_instruction[component_name][prompt_metadata_type]['variables']
                    
                    for para_no in range(1, count_number_of_passages+1):
                        template_text = await async_get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var=self.rand_var)
                        buffer.append({
                            "instruction statement": f"Generate para {para_no} of {count_number_of_passages}:\n{template_text}",
                            "output": self.component_instruction[component_name][prompt_metadata_type]['output']
                        })
            else:
                # Special handling for Multi-Source Reasoning (MSR)
                if self.question_type == 'Multi-Source Reasoning':
                    buffer.extend(await self._handle_msr_metadata(component_name, prompt_metadata_type))
                else:
                    # Standard non-MSR metadata (Tables, Charts, etc.)
                    for prompt_metadata_item in self.prompt_details['metadata-type'][prompt_metadata_type]:
                        file_name = self.component_instruction[component_name][prompt_metadata_type]['file-name']
                        variables = self.component_instruction[component_name][prompt_metadata_type]['variables']
                        template_text = await async_get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, prompt_metadata_type, prompt_metadata_item, rand_var=self.rand_var)
                        buffer.append({
                            "instruction statement": template_text,
                            "output": self.component_instruction[component_name][prompt_metadata_type]['output'],
                            'file-name': file_name
                        })
        return buffer

    async def _handle_msr_metadata(self, component_name: str, prompt_metadata_type: str) -> List[Dict]:
        """Specific logic for extracting MSR sources and skills."""
        from io_utils import async_get_Component_Template
        from db_artilaries import artilaries
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
            
            base_template = await async_get_Component_Template(
                component_name, file_name, 
                self.prompt_details['exam'], self.prompt_details['section'], 
                self.prompt_details['question-type'], variables, 
                meta_type, metadata_item, 
                rand_var=self.rand_var
            )
            
            theme = parts[1] if len(parts) > 1 else 'Business scenario'
            
            # Fetch MSF config from DB
            msr_config = await artilaries.get_component_data('QuestionMetadata', 'msr_source_instructions.json')
            if msr_config:
                 msr_config_dict = json.loads(msr_config)
            else:
                 # Fallback
                 msr_config_dict = {'instruction_template': "{base_template}\n\n[MSR Source {source_num}]: {source_type} focused on {focused_skill} in {theme} context."}
            
            instruction_with_context = msr_config_dict['instruction_template'].format(
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


    async def _handle_options(self, component_name: str) -> Dict:
        """Handles QuestionOptions/Answer logic."""
        from io_utils import async_get_Component_Template
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

                # Dynamic Schema Allocation for Blanks
                if self.prompt_details['option'] == 'blank':
                    parsed_tags = self.prompt_details.get('parsed_tags', {})
                    sub_topic = parsed_tags.get('Sub-topic/Focused Skill', '') if parsed_tags else ''
                    # Also check instruction/prompt for type hints if tags parsed incorrectly
                    instruction_str = self.prompt_details.get('instruction_str', '')
                    
                    if 'TC-1' in sub_topic or 'TC-1' in instruction_str:
                         file_name = 'blank-single-question-option-answer.txt.template'
                    elif 'TC-2' in sub_topic or 'TC-2' in instruction_str:
                         file_name = 'blank-double-question-option-answer.txt.template' 
                    elif 'TC-3' in sub_topic or 'TC-3' in instruction_str:
                         file_name = 'blank-triple-question-option-answer.txt.template'
                    elif self.prompt_details['question-type'] == 'Graphic Interpretation':
                         # Default GI to double blank for now
                         file_name = 'blank-double-question-option-answer.txt.template'

                # Unified template handles single/multi blank selection via conditionals
                template_text = await async_get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, rand_var=self.rand_var)

                return {
                    'instruction statement': template_text,
                    'output': output,
                    'file-name': file_name,
                    'option-type': self.prompt_details['option']
                }
        raise ValueError(f"No matching option instruction found for component '{component_name}', option type '{self.prompt_details['option']}', question type '{self.prompt_details['question-type']}'")

    async def _handle_generic_component(self, component_name: str) -> Dict:
        """Handles other components via recursion through instruction list."""
        from io_utils import async_get_Component_Template
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
                    'instruction statement': await async_get_Component_Template(component_name, file_name, self.prompt_details['exam'], self.prompt_details['section'], self.prompt_details['question-type'], variables, rand_var=self.rand_var),
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
        
        # DEFENSIVE FIX: Ensure prompt is a string, and extract extra info if tuple
        prompt_val = self.prompt_details.get('prompt')
        if isinstance(prompt_val, tuple):
             self.prompt_details['prompt'] = prompt_val[0]
             # If instruction_str or parsed_tags not already present, extract them
             if not self.prompt_details.get('instruction_str') and len(prompt_val) > 1:
                 self.prompt_details['instruction_str'] = prompt_val[1]
             if not self.prompt_details.get('parsed_tags') and len(prompt_val) > 2:
                 self.prompt_details['parsed_tags'] = prompt_val[2]

        self.generator_session = generator_session
        self.target_question_type = target_question_type
        self.question_type = prompt_details['question-type']
        self._log_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'log_json_files',
            'selected_questions'
        )
        self.rand_var = None

    async def get_question_data(self) -> Tuple[dict, dict]:
        """Main entry point to generate data for this question."""
        
        # 0. Capture Clean Prompt for Tags (Prevention of Leaks)
        self.clean_prompt_for_tags = self.prompt_details['prompt']

        # 1. Dynamic Difficulty Injection
        await self._inject_difficulty()
        
        # 1b. Inject Context (Vocab + Scenarios)
        await self._inject_context_and_vocab()

        # 2. Variable initialization
        if self.question_type == 'Text Completion':
            self.rand_var = self.prompt_details['prompt'].split(' - ', 1)[0].strip('<>')
        
        component_instruction = all_question_structure[1]
        question_components = list(all_question_structure[0][self.prompt_details['type']])
        
        if not self.prompt_details.get('metadata-type', None):
            if 'QuestionMetadata' in question_components:
                question_components.remove('QuestionMetadata')

        # 3. Get Templates (Using the new class)
        # The constructor no longer calculates templates immediately
        template_manager = ManageComponentTemplates(
            question_components=question_components,
            prompt_details=self.prompt_details,
            component_instruction=component_instruction,
            rand_var=self.rand_var
        )
        await template_manager.generate_all_templates()
        component_calls = template_manager.templates

        result_buffer, stats = await self._generate_components(component_calls)

        # 5. Handle Recursion (Child Questions)
        child_stats = await self._handle_child_questions(result_buffer)
        
        # Accumulate child stats
        stats['input_tokens'] += child_stats['input_tokens']
        stats['output_tokens'] += child_stats['output_tokens']
        stats['api_calls'] += child_stats['api_calls']

        # 6. Logging and Recording
        result_buffer['prompt'] = self.clean_prompt_for_tags
        result_buffer['question-type'] = self.question_type
        
        # Inject DB-required fields
        try:
             # Parse difficulty from prompt details or fallback
             if 'difficulty' in self.prompt_details:
                 result_buffer['difficulty'] = self.prompt_details['difficulty']
             elif 'difficulty' not in result_buffer:
                 # Attempt to extract from 'difficulty_level: <N>' in nomenclature if available
                 match = re.search(r'difficulty_level:\s*(\d+)', self.prompt_details.get('prompt', ''))
                 if match:
                     result_buffer['difficulty'] = int(match.group(1))
                 else:
                     result_buffer['difficulty'] = 1 # Default
        except:
             result_buffer['difficulty'] = 1

        # Tags Parsing Logic
        tags = []
        q_type_meta = self.prompt_details.get('type') # 'parent', 'child', or 'simple' (implied)
        result_buffer['options_type'] = self.prompt_details.get('option', 'single')

        def clean_tag(tag_str: str) -> str:
            """Removes < and > from tag strings"""
            return tag_str.replace('<', '').replace('>', '')

        try:
            parsed = self.prompt_details.get('parsed_tags', {})
            theme = parsed.get('Theme')
            topic = parsed.get('Topic')
            skill = parsed.get('Sub-topic/Focused Skill') or parsed.get('Focused Skill') or parsed.get('sub-topic')
            
            if q_type_meta == 'child':
                # Requirement: child only gets sub-topic
                if skill:
                    tags.append(clean_tag(f"sub-topic: {skill}"))
            
            elif q_type_meta == 'parent':
                # Requirement: parent gets type, theme, topic
                tags.append(clean_tag(f"question-type: {self.question_type}"))
                if theme:
                    tags.append(clean_tag(f"theme: {theme}"))
                
                # Fallback: if Topic is missing, use Skill (common in Verbal)
                effective_topic = topic or skill
                if effective_topic:
                    tags.append(clean_tag(f"topic: {effective_topic}"))
            
            else:
                # Simple requirement: all three [question-type, theme, topic]
                tags.append(clean_tag(f"question-type: {self.question_type}"))
                if theme:
                    tags.append(clean_tag(f"theme: {theme}"))
                
                # Fallback: if Topic is missing, use Skill
                effective_topic = topic or skill
                if effective_topic:
                    tags.append(clean_tag(f"topic: {effective_topic}"))

        except Exception as e:
            print(f"Warning: Tag parsing failed: {e}")
            tags.append(f"question-type: {self.question_type}") # Fallback

        # CRITICAL FIX: Assign tags to result_buffer before recording!
        result_buffer['tags'] = list(set(tags))

        return result_buffer, stats

    async def _inject_difficulty(self):
        from db_artilaries import artilaries
        try:
            difficulty_levels = await artilaries.get_difficulty_levels()
            qt = self.question_type
            
            # Determine Domain
            if qt in ["Data Sufficiency", "Problem Solving Simple", "Problem Solving Meta", "Numerical Entry", "Quantitative Comparison"]:
                domain = "Quants"
            elif qt in ["Sentence Equivalence", "Text Completion", "Reading Comprehension"]:
                domain = "Verbal"
            elif qt in ["Multi-Source Reasoning", "Two-Part Analysis", "Table Analysis", "Graphic Interpretation"]:
                domain = "Integrated Reasoning"
            else:
                domain = None

            # Ensure prompt is a string before regex search
            current_prompt = self.prompt_details['prompt']
            if isinstance(current_prompt, tuple):
                current_prompt = current_prompt[0]
                self.prompt_details['prompt'] = current_prompt

            match = re.search(r'difficulty_level:\s*<(\d)>', current_prompt)
            if domain and match:
                level = match.group(1)
                instruction = difficulty_levels.get(domain, {}).get(level)
                if instruction:
                    self.prompt_details['prompt'] += f"\n\n[Difficulty Instruction]: {instruction}"
        except Exception as e:
            print(f"Warning: Failed to inject difficulty instruction: {e}")

    async def _inject_context_and_vocab(self):
        """
        Injects Vocabulary and Scenario Context into the prompt *before* generation.
        """
        from db_artilaries import artilaries
        # --- VOCABULARY INJECTION ---
        if self.question_type in ['Text Completion', 'Reading Comprehension', 'Sentence Equivalence', 'Critical Reasoning', 'Sentence Correction']:
            try:
                vocab_data = await artilaries.get_config('vocabulary')
                if vocab_data:
                    exam = self.prompt_details.get('exam', 'GRE')
                    if exam not in vocab_data: exam = 'GRE'
                    
                    current_difficulty = self.prompt_details.get('difficulty', 1)
                    diff_key = str(max(1, min(5, current_difficulty)))
                    
                    word_list = vocab_data.get(exam, {}).get(diff_key, [])
                    
                    if word_list:
                        count = 15 if self.question_type in ['Reading Comprehension', 'Critical Reasoning'] else 10
                        selected_words = random.sample(word_list, min(len(word_list), count))
                        
                        vocab_instruction = f"\n\n[Vocabulary Instruction]: Integrate the following words naturally into the text (or options where appropriate): {', '.join(selected_words)}."
                        
                        # Ensure prompt is a string before appending
                        if isinstance(self.prompt_details['prompt'], tuple):
                            self.prompt_details['prompt'] = self.prompt_details['prompt'][0]
                            
                        self.prompt_details['prompt'] += vocab_instruction
            except Exception as e:
                print(f"Warning: Failed to inject vocabulary: {e}")


    async def _generate_components(self, component_calls: list) -> Tuple[dict, dict]:
        from io_utils import async_get_Question_Template
        from db_artilaries import artilaries
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
                     sys_instruct = await async_get_Question_Template(
                        question_component="SystemInstruction",
                        filename=template_name,
                        exam_type=self.prompt_details['exam'],
                        Section_name=self.prompt_details['section'],
                        question_type=self.question_type,
                        variable=None
                     )

                     # --- INJECT COMPLEXITY GUIDELINES ---
                     try:
                         # Load guidelines from DB
                         all_guidelines = await artilaries.get_complexity_guidelines()
                         
                         # Determine domain for complexity
                         domain = "Quants" if self.question_type in ["Data Sufficiency", "Problem Solving Simple", "Problem Solving Meta", "Numerical Entry", "Quantitative Comparison"] else \
                                  "Verbal" if self.question_type in ["Sentence Equivalence", "Text Completion", "Reading Comprehension", "Critical Reasoning"] else \
                                  "Integrated Reasoning"

                         guidelines = all_guidelines.get(domain, [])
                         
                         if guidelines:
                             guidelines_text = "\n".join(guidelines)
                             sys_instruct += f"\n\n## COMPLEXITY GUIDELINES (STRICT COMPLIANCE REQUIRED)\n{guidelines_text}\n"
                     except Exception as e:
                         print(f"Warning: Failed to inject complexity guidelines: {e}")

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

            source_info = None
            if comp_type == 'QuestionMetadata' and self.question_type == 'Multi-Source Reasoning':
                source_info = {k: call.get(k) for k in ['source_number', 'source_type', 'focused_skill'] if k in call}
            
            # --- COMPONENT GENERATION & RETRY LOOP ---
            max_attempts = 2
            attempt = 1
            while attempt <= max_attempts:
                try:
                    # Async generation call
                    parsed_data, stats = await self.generator_session.generate_component(
                        instruction_statement=call['instruction statement'],
                        expected_output=call['output'],
                        context=context
                    )
                    
                    # Accumulate stats
                    total_stats['input_tokens'] += stats['input_tokens']
                    total_stats['output_tokens'] += stats['output_tokens']
                    total_stats['api_calls'] += 1
                    
                    # Store result
                    if comp_type == 'QuestionMetadata':
                         if 'metadata' not in result_buffer:
                              result_buffer['metadata'] = []

                         # Guard: if LLM returned string, wrap in dict
                         if isinstance(parsed_data, str):
                              parsed_data = {'raw_content': parsed_data}

                         if isinstance(parsed_data, dict) and self.question_type == 'Multi-Source Reasoning' and source_info:
                              parsed_data.update(source_info)

                         result_buffer['metadata'].append(parsed_data)
                    else:
                         # For question and options/answer, we expect a dict based on expected_output.
                         # If it's a raw string, wrap it.
                         if isinstance(parsed_data, str):
                              parsed_data = {comp_type.lower().replace('/', '_'): parsed_data}

                         if isinstance(parsed_data, dict):
                              # Sometimes the LLM returns {"question": "..."} instead of {"questiontext": "..."}
                              # To be safe, we merge whatever dictionary keys it returned into result_buffer,
                              # AND we also attempt to capture it under `generated_question_text` for chaining.
                              if comp_type == 'QuestionText':
                                   # Get the first value in the dict as the fallback question text
                                   fallback_text = list(parsed_data.values())[0] if parsed_data else ""
                                   generated_question_text = parsed_data.get('question_text') or \
                                                             parsed_data.get('questiontext') or \
                                                             parsed_data.get('question') or \
                                                             fallback_text
                                   # Force standard key names for DB
                                   parsed_data['questiontext'] = generated_question_text

                              elif comp_type == 'QuestionSolution':
                                   fallback_sol = list(parsed_data.values())[0] if parsed_data else ""
                                   sol_text = parsed_data.get('solution') or parsed_data.get('questionsolution') or fallback_sol
                                   parsed_data['questionsolution'] = sol_text

                              result_buffer.update(parsed_data)
                         else:
                              print(f"      {prettify('Warning:', 'Yellow')} {comp_type} returned unexpected type {type(parsed_data).__name__} — skipping.")
                    
                    break # Success, exit retry loop
                    
                except Exception as e:
                    print(f"      {prettify('Error:', 'Red')} Component {comp_type} generation failed (Attempt {attempt}/{max_attempts}): {e}")
                    attempt += 1
                    if attempt > max_attempts:
                         print(f"      {prettify('Critical:', 'Red', True)} {comp_type} failed after {max_attempts} attempts.")
                         total_stats['failed'] = True
                    else:
                        # On rate-limit (429): wait 10s before retry so Mercury's
                        # server-side window has time to clear — last-resort safety net
                        err_str = str(e)
                        if '429' in err_str or 'rate_limit' in err_str.lower():
                            import asyncio as _aio
                            print(f"      {prettify('Backoff:', 'Yellow')} 429 detected — waiting 10s before retry...")
                            await _aio.sleep(10)

        return result_buffer, total_stats

    async def _handle_child_questions(self, result_buffer: dict) -> dict:
        total_child_stats = {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
        
        if self.prompt_details.get('type') == 'parent':
            parent_metadata = result_buffer.get('metadata')
            child_prompt_data = []
            
            child_prompts = self.prompt_details.get('child-prompt')
            if not child_prompts:
                 print(f"      {prettify('Warning:', 'Yellow')} Parent question had no 'child-prompt' list. Skipping children.")
                 return total_child_stats

            for child_prompt in child_prompts:
                child_prompt_details = {
                    'type': 'child',
                    'exam': self.prompt_details['exam'],
                    'section': self.prompt_details['section'],
                    'question-type': child_prompt.get('question-type', self.prompt_details['question-type']),
                    'option': child_prompt['option'],
                    'prompt': child_prompt['prompt']
                }

                child_manager = ManageQuestionData(
                    prompt_details=child_prompt_details,
                    generator_session=self.generator_session, # Share session
                    target_question_type=self.target_question_type
                )
                child_data, child_stats = await child_manager.get_question_data()
                child_prompt_data.append(child_data)
                
                # Accumulate stats
                total_child_stats['input_tokens'] += child_stats['input_tokens']
                total_child_stats['output_tokens'] += child_stats['output_tokens']
                total_child_stats['api_calls'] += child_stats['api_calls']
                
            result_buffer['child-questions'] = child_prompt_data
            
        return total_child_stats


