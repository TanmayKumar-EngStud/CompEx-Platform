import os
import sys
import json
import time
import random
import re

# Standalone imports (no parent dir needed)
from io_utils import get_json, prettify, get_Component_Template
from difficulty_pool import get_difficulty_pool
from prepare_prompts import PromptPrep
from question_manager import ManageComponentTemplates

def load_template_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def get_next_paper_id(exam, output_dir):
    """Finds the next available paper ID (e.g., GRE_01, GRE_02)."""
    exam_dir = os.path.join(output_dir, exam)
    os.makedirs(exam_dir, exist_ok=True)
    
    existing_files = os.listdir(exam_dir)
    pattern = re.compile(f"{exam}_(\d{{2}})\.json")
    
    max_id = 0
    for f in existing_files:
        match = pattern.match(f)
        if match:
            max_id = max(max_id, int(match.group(1)))
    
    return f"{max_id + 1:02d}"

def select_exam_and_difficulty():
    """Interactively select Exam Type and Difficulty."""
    print(f"\n{prettify('CONFIGURATION SLECTION', 'Cyan', True)}")
    
    # Select Exam
    while True:
        exam_input = input("Select Exam Type (GRE/GMAT) > ").strip().upper()
        if exam_input in ['GRE', 'GMAT']:
            break
        print("Invalid selection. Please enter GRE or GMAT.")
        
    # Select Difficulty
    while True:
        try:
            diff_input = input("Select Target Difficulty (1-5) > ").strip()
            difficulty = int(diff_input)
            if 1 <= difficulty <= 5:
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    return exam_input, difficulty

def parse_tags(prompt_str, question_type):
    """Parsed tags from prompt string to match main system logic."""
    tags = []
    def clean_tag(tag_str):
        return tag_str.replace('<', '').replace('>', '')
    
    tags.append(clean_tag(f"type: {question_type}"))
    
    # Verbal Types
    if question_type in ['Sentence Equivalence', 'Text Completion', 'Reading Comprehension', 'Critical Reasoning']:
        theme_match = re.search(r'Theme:\s*(.*?)(?:\s*\||$)', prompt_str)
        if theme_match:
            tags.append(clean_tag(f"theme: {theme_match.group(1).strip()}"))
        topic_match = re.search(r'Topic:\s*(.*?)(?:\s*\||$)', prompt_str)
        if topic_match:
            tags.append(clean_tag(f"topic: {topic_match.group(1).strip()}"))
    else:
        # Quants (Hyphen separated)
        parts = prompt_str.split(' - ')
        if len(parts) > 0: tags.append(clean_tag(f"topic: {parts[0]}"))
        if len(parts) > 1: tags.append(clean_tag(f"theme: {parts[1]}"))
        
    return tags

def process_exam_generation():
    # 1. Configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(base_dir, 'papers')
    cmd_template = load_template_file(os.path.join(base_dir, 'primary_commands_to_Gemini.template.txt'))
    
    exam_definition = get_json('exam_definition')[0]
    qt_info = get_json('question_type_info')[0]
    all_question_structure = get_json('question_component_types')[0]
    component_instruction_db = all_question_structure[1] # "component_type_templates"
    
    # 2. Interactive Selection
    target_exam, target_difficulty = select_exam_and_difficulty()
    
    # Filter for target exam
    target_sections = exam_definition.get(target_exam, {})
    if not target_sections:
        print(f"Error: No definition found for {target_exam}")
        return

    exam = target_exam
    sections = target_sections
    
    paper_id = get_next_paper_id(exam, papers_dir)
    paper_data = {} # {section_id: {questions: []}}
    
    print(f"\n{prettify(f'STARTING GENERATION FOR {exam}_{paper_id} (Diff: {target_difficulty})', 'Cyan', True)}")
    
    for section_id, section_data in sections.items():
        section_name = section_data['name']
        total_needed = section_data['total']
        paper_data[section_id] = {'section': section_name, 'questions': []}
        
        print(f"\n{prettify(f'Section: {section_name}', 'Yellow')}")
        
        # Difficulty Pool (Override with target difficulty mostly, but keep some variance)
        # Actually, user asked for "Target Difficulty". Let's generate a pool centered around it.
        # Or just pass target_difficulty to get_difficulty_pool as 'mock_level'
        difficulties = get_difficulty_pool(exam, section_name, total_needed + 5, target_difficulty)
        
        for q_type in section_data['question types']:
            count = section_data[q_type]
            q_info = PromptPrep._must_get(qt_info, q_type, 'qt_info')
            
            print(f"  > Processing {count} questions of type {prettify(q_type, 'Magenta')}")
            
            for _ in range(count):
                if not difficulties: 
                     # Refill if empty
                     difficulties = [target_difficulty] * 10 
                
                diff = difficulties.pop()
                
                # 3. Get Prompt
                nomenclature = q_info["nomenclature"]
                
                # Note: PromptPrep might return tuple now! We need to handle it.
                # In main.py: prompt, instruction_str, parsed_tags = PromptPrep._nomenclature_to_prompt_mapping(...)
                # In run.py (old code): `prompt_str = PromptPrep._nomenclature_to_prompt_mapping(...)`
                # We expect PromptPrep to now return a TUPLE (str, str, dict) based on my recent changes.
                
                prompt_res = PromptPrep._nomenclature_to_prompt_mapping(nomenclature, q_type, diff)
                
                if isinstance(prompt_res, tuple):
                    prompt_str = prompt_res[0]
                    instruction_str = prompt_res[1]
                    # We can use parsed_tags if we want, but parse_tags function below does regex.
                    # Ideally we should use the dict returned.
                    parsed_tags_dict = prompt_res[2] if len(prompt_res) > 2 else {}
                else:
                    prompt_str = prompt_res
                    instruction_str = ""
                    parsed_tags_dict = {}
                
                if not prompt_str:
                        print(f"Error: No prompt found for {nomenclature}")
                        continue

                option_val = q_info.get('options')
                if isinstance(option_val, dict):
                    option_val = random.choices(
                        list(option_val.keys()), weights=list(option_val.values()))[0]

                # 4. Interactive Loop for Components
                # We need to simulate the component generation flow
                prompt_details = {
                    'exam': exam,
                    'section': section_name,
                    'question-type': q_type,
                    'type': q_info['type'],
                    'difficulty': diff,
                    'prompt': prompt_str,
                    'instruction_str': instruction_str,
                    'option': option_val,
                    'child-prompt': q_info.get('child-question'),
                    'metadata-type': q_info.get('has-metadata') and PromptPrep._selective_metadata_info(q_type)
                }
                
                # Handle Random Var for Text Completion
                rand_var = None
                if q_type == 'Text Completion':
                    rand_var = prompt_str.split(' - ', 1)[0].strip('<>')

                # Get Components List
                question_components = list(all_question_structure[0][q_info['type']])
                
                # Metadata Filtering
                if not prompt_details.get('metadata-type'):
                        if 'QuestionMetadata' in question_components:
                            question_components.remove('QuestionMetadata')

                # Generate Templates using ManageComponentTemplates
                # This class resolves specific instructions for us
                template_manager = ManageComponentTemplates(
                    question_components=question_components,
                    prompt_details=prompt_details,
                    component_instruction=component_instruction_db,
                    rand_var=rand_var
                )
                
                # --- FLATTENED STRUCTURE ---
                current_question_data = {
                    'prompt': prompt_str,
                    'difficulty': diff,
                    'question-type': q_type,
                    'tags': parse_tags(prompt_str, q_type) # Keeping this or using parsed_tags_dict?
                }
                
                # Execute each component INTERACTIVELY
                for component_group in template_manager.templates:
                    for comp_name, comp_data_list in component_group.items():
                        # Normalize to list
                        if not isinstance(comp_data_list, list):
                            comp_data_list = [comp_data_list]
                            
                        results = []
                        for idx, comp_data in enumerate(comp_data_list):
                            instruction = comp_data['instruction statement']
                            output_fmt = comp_data['output']
                            
                            # --- THE INTERACTIVE PART ---
                            sys_instruct = "You are an expert exam generator. Follow the component instructions exactly."
                            
                            # Append explicit instruction string if present (mimicking main.py logic)
                            augmented_instruction = instruction
                            if instruction_str:
                                augmented_instruction += f"\n\n{instruction_str}"
                            augmented_instruction += f"\n\n[Context & Constraints]: {prompt_str}"

                            # 2. Format Command
                            command = cmd_template.format(
                                system_instruction=sys_instruct,
                                component_instruction=augmented_instruction, # Use augmented
                                expected_output=output_fmt
                            )
                            
                            # 3. PRINT COMMAND TO AGENT
                            print("\n" + "="*80)
                            print(f"Generate {comp_name} ({idx+1}/{len(comp_data_list)})")
                            print(f"{prettify('PROMPT CONTEXT:', 'Yellow')}")
                            print(f"{prompt_str}")
                            if instruction_str:
                                print(f"{prettify('INSTRUCTION:', 'Back, Magenta')}")
                                print(f"{instruction_str}")
                            print("-" * 40)
                            print(command)
                            print("="*80 + "\n")
                            
                            # 4. WAIT FOR AGENT INPUT
                            print(f"{prettify('WAITING FOR JSON INPUT...', 'Green', True)}")
                            while True:
                                try:
                                    user_input = input("Paste JSON Response (one line preferred) > ")
                                    parsed = json.loads(user_input)
                                    results.append(parsed)
                                    print("✅ Input Received.")
                                    break
                                except json.JSONDecodeError:
                                    print("❌ Invalid JSON. Please try again.")
                                except EOFError:
                                    sys.exit(0)
                        
                        # Store result FLATTENED
                        if len(results) == 1:
                            current_question_data[comp_name] = results[0]
                        else:
                            current_question_data[comp_name] = results
                            
                paper_data[section_id]['questions'].append(current_question_data)
                
                # 5. Save Paper Incrementally
                final_path = os.path.join(papers_dir, exam, f"{exam}_{paper_id}.json")
                with open(final_path, 'w', encoding='utf-8') as f:
                    json.dump(paper_data, f, indent=2, ensure_ascii=False)
                print(f"\n{prettify(f'Saved progress to: {final_path}', 'Green')}")

if __name__ == "__main__":
    process_exam_generation()
