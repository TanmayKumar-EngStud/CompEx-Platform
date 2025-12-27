
"""
    Main Mega: Generates multiple sets of papers in parallel.
    Set 1: Diff 1, isMock False
    Set 2: Diff 2, isMock True
    Set 3: Diff 3, isMock False
    Set 4: Diff 4, isMock True
    Set 5: Diff 5, isMock False
    ...
"""
import os
import random
import json
import logging
import concurrent.futures
from typing import Any, Optional, Dict

# Reuse imports from existing modules
from difficulty_pool import get_difficulty_pool
from io_utils import get_json, prettify
from prepare_prompts import PromptPrep
from generator import GenQ
from db_integration import save_paper_to_db, save_analytics_record

# --- Configuration ---
NUMBER_OF_SETS = 5

# Ensure output directory exists
MEGA_PAPER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper', 'mega_papers')
os.makedirs(MEGA_PAPER_DIR, exist_ok=True)

# Shared definitions (load once to save I/O)
EXAM_DEFINITION, QT_INFO, PROMPT_COMPONENT_INFO = get_json(
    'exam_definition', 'question_type_info', 'prompt_component_info')

def generate_single_paper(set_index: int, difficulty: int, is_mock: bool):
    """
    Encapsulated generation logic for a single paper set.
    """
    try:
        print(f"\n[Set {set_index}] Starting generation: Difficulty={difficulty}, Mock={is_mock}")
        
        # 1. Prepare Prompts Dictionary for this run
        # Note: Prompts dictionary structure is {exam: {section_num: {...}}}
        current_prompts = {}
        sorted_exams = sorted(EXAM_DEFINITION.items(), key=lambda x: x[0], reverse=True)

        for exam, sections in sorted_exams:
            current_prompts[exam] = {}
            for section_number, section in sections.items():
                section_name = section['name']
                n_items = section['total']
                
                # Get difficulty pool for this specific run's difficulty level
                difficulty_list = get_difficulty_pool(
                    exam, section_name, n_items + 5, difficulty)

                current_prompts[exam][section_number] = {}
                current_prompts[exam][section_number]['section'] = section_name
                
                total_prompt_count = 0 
                # Keep track for shuffling later
                
                for question_type in section['question types']:
                    question_type_info = PromptPrep._must_get(QT_INFO, question_type, '@combination-variant.json')
                    count_of_this_question_type = section[question_type]
                    
                    current_prompts[exam][section_number][question_type] = {
                        "has-metadata": question_type_info['has-metadata'],
                        'type': question_type_info['type'],
                        'prompts': []
                    }
                    
                    prompt_count = 0
                    while prompt_count < count_of_this_question_type:
                        PromptPrep._must_get(section, question_type, f'section({section_number}) -> {section_name}: @exam_definition.json')

                        if not difficulty_list:
                            # Fallback if pool exhausted
                            current_diff = difficulty
                        else:
                            current_diff = difficulty_list.pop()
                            
                        nomenclature = question_type_info["nomenclature"]

                        try:
                            # Generate Prompt/Instruction
                            prompt, instruction_str, parsed_tags = PromptPrep._nomenclature_to_prompt_mapping(
                                nomenclature, question_type, current_diff)
                        except ValueError as e:
                            print(f"[Set {set_index}] Error generating prompt: {e}")
                            continue # Skip this prompt attempt

                        if prompt is None:
                            print(f"[Set {set_index}] Got None prompt for {question_type}")
                            continue

                        prompt_buffer = {
                            'prompt': prompt,
                            'instruction_str': instruction_str,
                            'parsed_tags': parsed_tags,
                            'difficulty': current_diff,
                        }

                        # Handle Options logic
                        if question_type_info.get('options'):
                            option = question_type_info['options']
                            if isinstance(option, dict):
                                option = random.choices(list(option.keys()), weights=list(option.values()))[0]
                            prompt_buffer['option'] = option

                        prompt_count += 1

                        # Handle Child Questions
                        if question_type_info.get('child-question', None):
                            prompt_count -= 1 # Parent doesn't count towards total item limit usually?
                            # Logic from main.py:
                            difficulty_list.append(0) # placeholder?
                            
                            child_count = PromptPrep._get_child_count(
                                nomenclature, question_type=question_type, parent_prompt=prompt, child_info=question_type_info['child-question'])
                            
                            prompt_buffer['child-prompt'] = []
                            for _ in range(child_count):
                                prompt_count += 1
                                child_diff = random.randint(max(current_diff-1, 1), min(current_diff+1, 5))
                                child_qs_info = question_type_info['child-question']
                                child_nom = child_qs_info['nomenclature']

                                try:
                                    child_prompt, _, _ = PromptPrep._nomenclature_to_prompt_mapping(
                                        child_nom, child_qs_info.get('question-type', question_type), child_diff)
                                except Exception as e:
                                    print(f"[Set {set_index}] Child prompt error: {e}")
                                    continue
                                
                                child_opt = child_qs_info['options']
                                if isinstance(child_opt, dict):
                                    child_opt = random.choices(list(child_opt.keys()), weights=list(child_opt.values()))[0]

                                child_prompt_buffer = {
                                    'prompt': child_prompt,
                                    'option': child_opt,
                                    'difficulty': child_diff,
                                    'question-type': child_qs_info.get('question-type', question_type)
                                }
                                prompt_buffer['child-prompt'].append(child_prompt_buffer)
                            
                            if difficulty_list: difficulty_list.pop()

                        # Handle Metadata
                        if question_type_info.get('has-metadata'):
                            meta_count = question_type_info.get('meta-count', 1)
                            meta_options = PromptPrep._selective_metadata_info(question_type)
                            metadata_buffer = {}

                            # TPA Logic
                            if question_type == "Two-Part Analysis":
                                if 'passage' in meta_options:
                                    metadata_buffer['passage'] = [random.choice(meta_options['passage'])]
                                visual_cats = [k for k in meta_options.keys() if k in ['tables', 'charts']]
                                if visual_cats:
                                    cat = random.choice(visual_cats)
                                    metadata_buffer[cat] = [random.choice(meta_options[cat])]
                            else:
                                for _ in range(meta_count):
                                    cat = random.choice(list(meta_options.keys()))
                                    if metadata_buffer.get(cat) is None:
                                        metadata_buffer[cat] = [random.choice(meta_options[cat])]
                                    else:
                                        metadata_buffer[cat].append(random.choice(meta_options[cat]))
                            
                            prompt_buffer['metadata-type'] = metadata_buffer

                        current_prompts[exam][section_number][question_type]['prompts'].append(prompt_buffer)
                    
                    total_prompt_count += prompt_count
                
                # Shuffle prompts
                PromptPrep._remove_extra_and_shuffle_created_prompts(
                     current_prompts[exam][section_number], total_prompt_count - n_items)

        # 2. Generate Content using GenQ
        # print(f"[Set {set_index}] Prompt preparation complete. Invoking Generator...")
        # Note: GenQ constructor takes the dictionary
        gen = GenQ(current_prompts)
        
        # IMPORTANT: GenQ.generate() writes files to 'log_json_files/paper/'. 
        # We want to move or save them to 'mega_papers'.
        # However, GenQ.generate returns 'paper_set'. We can save that manually.
        complete_paper = gen.generate()
        
        # 3. Save to File
        # Format: <examname>_<set number>.json
        # 'complete_paper' is { "GMAT": {...}, "GRE": {...} }
        for exam_key, paper_content in complete_paper.items():
            filename = f"{exam_key}_{set_index}.json"
            filepath = os.path.join(MEGA_PAPER_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({exam_key: paper_content}, f, indent=2, ensure_ascii=False) # Wrap manually to match DB expectation? 
                # Wait, GenQ output is already { "Exam": {...} }?
                # GenQ.generate() returns self.paper_set which is initialized as { exam: {} }
                # So complete_paper is { "GMAT": {...}, "GRE": {...} }
                # But when iterating, paper_content is just the inner dict?
                # We should save { "GMAT": paper_content } to match store_as_mock logic
                # Actually, check main.py. main calls save_paper_to_db(complete_paper).
                # here we want tailored files.
                pass

        print(f"[Set {set_index}] Saving to Database...")
        save_paper_to_db(complete_paper, is_mock=is_mock, difficulty=difficulty)
        
        if gen.last_run_stats:
            save_analytics_record(gen.last_run_stats, difficulty, is_mock)

        print(f"[Set {set_index}] Completed successfully.")
        return True

    except Exception as e:
        print(f"[Set {set_index}] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print(f"--- Mega Paper Generator (Sets: {NUMBER_OF_SETS}) ---")
    
    # Using ThreadPoolExecutor for I/O bound tasks (API calls)
    # Be mindful of API rate limits!
    max_workers = 3 # Limit concurrency to avoid rate limits
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(1, NUMBER_OF_SETS + 1):
            # Logic:
            # Difficulty: (i-1) % 5 + 1  -> 1, 2, 3, 4, 5, 1...
            # Mock: i % 2 == 0 -> False (1), True (2), False (3)...
            diff = (i - 1) % 5 + 1
            is_mock = (i % 2 == 0)
            
            futures.append(executor.submit(generate_single_paper, i, diff, is_mock))
        
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
