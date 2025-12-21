import os
import sys
import json
import time
import random
import re

# Import parent modules
try:
    from utils_import import parent_dir
except ImportError:
    import utils_import

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

def process_exam_generation():
    # 1. Configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(base_dir, 'papers')
    cmd_template = load_template_file(os.path.join(base_dir, 'primary_commands_to_Gemini.template.txt'))
    
    exam_definition = get_json('exam_definition')[0]
    qt_info = get_json('question_type_info')[0]
    all_question_structure = get_json('question_component_types')[0]
    component_instruction_db = all_question_structure[1] # "component_type_templates"
    
    mock_level = 4 # Default target difficulty
    
    # 2. Iterate Exams
    sorted_exams = sorted(exam_definition.items(), key=lambda x: x[0], reverse=True)
    
    for exam, sections in sorted_exams:
        paper_id = get_next_paper_id(exam, papers_dir)
        paper_data = {} # {section_id: {questions: []}}
        
        print(f"\n{prettify(f'STARTING GENERATION FOR {exam}_{paper_id}', 'Cyan', True)}")
        
        for section_id, section_data in sections.items():
            section_name = section_data['name']
            total_needed = section_data['total']
            paper_data[section_id] = {'section': section_name, 'questions': []}
            
            print(f"\n{prettify(f'Section: {section_name}', 'Yellow')}")
            
            # Difficulty Pool
            difficulties = get_difficulty_pool(exam, section_name, total_needed + 5, mock_level)
            
            for q_type in section_data['question types']:
                count = section_data[q_type]
                q_info = PromptPrep._must_get(qt_info, q_type, 'qt_info')
                
                print(f"  > Processing {count} questions of type {prettify(q_type, 'Magenta')}")
                
                for _ in range(count):
                    if not difficulties: break
                    diff = difficulties.pop()
                    
                    # 3. Get Prompt
                    nomenclature = q_info["nomenclature"]
                    prompt_str = PromptPrep._nomenclature_to_prompt_mapping(nomenclature, q_type, diff)
                    
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
                    
                    current_question_data = {'prompt': prompt_str, 'difficulty': diff, 'type': q_type, 'components': {}}
                    
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
                                # 1. Get System Instruction
                                # (Simplified: We assume a generic system instruction or fetch one based on type)
                                sys_instruct = "You are an expert exam generator. Follow the component instructions exactly."
                                
                                # 2. Format Command
                                command = cmd_template.format(
                                    system_instruction=sys_instruct,
                                    component_instruction=instruction,
                                    expected_output=output_fmt
                                )
                                
                                # 3. PRINT COMMAND TO AGENT
                                print("\n" + "="*80)
                                print(f"Generate {comp_name} ({idx+1}/{len(comp_data_list)})")
                                print(f"{prettify('PROMPT CONTEXT:', 'Yellow')}")
                                print(f"{prompt_str}")
                                print("-" * 40)
                                print(command)
                                print("="*80 + "\n")
                                
                                # 4. WAIT FOR AGENT INPUT
                                print(f"{prettify('WAITING FOR JSON INPUT...', 'Green', True)}")
                                while True:
                                    try:
                                        # We expect the agent to paste one line (compressed JSON) or block of JSON
                                        # Since specific end token is hard, we read lines until we parse valid JSON?
                                        # Or simpler: Agent types "JSON_START" ... "JSON_END"?
                                        # Or simplest: standard input() reads one line. Agent pastes compressed JSON.
                                        
                                        user_input = input("Paste JSON Response (one line preferred) > ")
                                        
                                        # Attempt parse
                                        parsed = json.loads(user_input)
                                        results.append(parsed)
                                        print("✅ Input Received.")
                                        break
                                    except json.JSONDecodeError:
                                        print("❌ Invalid JSON. Please try again.")
                                    except EOFError:
                                        sys.exit(0)
                            
                            # Store result
                            if len(results) == 1:
                                current_question_data['components'][comp_name] = results[0]
                            else:
                                current_question_data['components'][comp_name] = results
                                
                    paper_data[section_id]['questions'].append(current_question_data)
                    
                    # 5. Save Paper Incrementally
                    final_path = os.path.join(papers_dir, exam, f"{exam}_{paper_id}.json")
                    with open(final_path, 'w', encoding='utf-8') as f:
                        json.dump(paper_data, f, indent=2, ensure_ascii=False)
                    print(f"\n{prettify(f'Saved progress to: {final_path}', 'Green')}")

if __name__ == "__main__":
    process_exam_generation()
