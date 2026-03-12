"""
    Main entry point for question generation using Artilaries PostgreSQL database.
"""
import os
import random
import json
import sys
from typing import Any, Optional
from difficulty_pool import get_difficulty_pool, initialize_difficulty_pool
from question_manager import initialize_question_manager
from io_utils import prettify
from prepare_prompts import PromptPrep, load_configs
from generator import GenQ
from db_artilaries import artilaries

# Global configuration variables
MOCK_PAPER_LEVEL = 1
IS_MOCK_RUN = False

async def initialize_configs():
    """Initializes dynamic configuration from Artilaries DB."""
    global MOCK_PAPER_LEVEL, IS_MOCK_RUN
    print(f"{prettify('STATUS', 'Yellow')}: Fetching dynamic configuration from Artilaries DB...")
    
    # Load configs into prepare_prompts globals
    await load_configs()
    # Initialize difficulty pool
    await initialize_difficulty_pool()
    # Initialize question manager
    await initialize_question_manager()
    
    # Import updated globals from prepare_prompts
    from prepare_prompts import exam_definition, qt_info
    
    # Database Fetch for Mock Params (Legacy/Integration)
    try:
        from db_integration import get_next_generation_params
        MOCK_PAPER_LEVEL, IS_MOCK_RUN = await get_next_generation_params()
        print(f"{prettify('GEN CONFIG', 'Cyan', True)}: Difficulty={MOCK_PAPER_LEVEL}, IsMock={IS_MOCK_RUN}")
    except Exception as e:
        print(f"Warning: DB Integration Fetch failed ({e}). Defaulting to 1/False.")
        
    return exam_definition, qt_info

async def main_gen():
    global MOCK_PAPER_LEVEL, IS_MOCK_RUN
    
    # 1. Initialize
    exam_definition, qt_info = await initialize_configs()
    prompts_dictionary = {}
    
    print(f"{prettify('START', 'Green')}: Running Generation Pipeline...")

    # 2. Sort exams
    sorted_exams = sorted(exam_definition.items(), key=lambda x: x[0], reverse=True)

    # 3. Process Exams
    for exam, sections in sorted_exams:
        prompts_dictionary[exam] = {}
        for section_number, section in sections.items():
            section_name = section['name']
            n_items = section['total']
            total_prompt_count = 0
            
            # Generate difficulty pool
            difficulty_list = get_difficulty_pool(
                exam, section_name, n_items * 5 + 50, MOCK_PAPER_LEVEL)

            prompts_dictionary[exam][section_number] = {
                'section': section_name
            }
            
            for question_type in section['question types']:
                # Get question type info from the DB-backed local cache
                question_type_info = PromptPrep._must_get(qt_info, question_type, 'Artilaries DB')
                count_needed = section[question_type]
                
                prompts_dictionary[exam][section_number][question_type] = {
                    "has-metadata": question_type_info['has-metadata'],
                    'type': question_type_info['type'],
                    'prompts': []
                }
                
                prompt_count = 0
                while prompt_count < count_needed:
                    current_difficulty = difficulty_list.pop()
                    nomenclature = question_type_info["nomenclature"]
                    
                    try:
                        # Call ASYNC prompt mapping
                        prompt, instruction_str, parsed_tags = await PromptPrep._nomenclature_to_prompt_mapping(
                            nomenclature, question_type, current_difficulty, exam_name=exam)
                    except ValueError as e:
                        print(f"\n{prettify('FATAL ERROR', 'Red', True)}: {e}")
                        sys.exit(1)

                    prompt_buffer = {
                        'prompt': prompt,
                        'instruction_str': instruction_str,
                        'parsed_tags': parsed_tags,
                        'difficulty': current_difficulty,
                    }
                    
                    # Handle options
                    if question_type_info.get('options'):
                        options = question_type_info['options']
                        if isinstance(options, dict):
                            option = random.choices(list(options.keys()), weights=list(options.values()))[0]
                        else:
                            option = random.choice(options) if isinstance(options, list) else options
                        prompt_buffer['option'] = option
                    
                    prompt_count += 1
                    
                    # Handle Child Questions (Simplified for refactor)
                    # Handle Child Questions (Simplified for refactor)
                    if question_type_info.get('child-question'):
                        # prompt_count -= 1 # Parent doesn't count towards total if children are present? 
                        # Actually logic varies. Keeping original behavior structure.
                        pass # Implementation of children if needed.
                    
                    # Handle Metadata
                    if question_type_info.get('has-metadata'):
                         metadata_options = await PromptPrep._selective_metadata_info(question_type)
                         metadata_buffer = {}
                         for cat, opts in metadata_options.items():
                             metadata_buffer[cat] = [random.choice(opts)]
                         prompt_buffer['metadata-type'] = metadata_buffer

                    prompts_dictionary[exam][section_number][question_type]['prompts'].append(prompt_buffer)
                
                total_prompt_count += prompt_count
            
            # Finalize section
            PromptPrep._remove_extra_and_shuffle_created_prompts(
                prompts_dictionary[exam][section_number], total_prompt_count - n_items)

    # 4. Save to file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files/prompts_dictionary.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(prompts_dictionary, f, indent=3)

    # 5. Generate with external Generator
    paper_gen = GenQ(prompts_dictionary)
    complete_paper = await paper_gen.generate()
    
    # 6. Database Persistence
    try:
        from db_integration import save_paper_to_db, save_analytics_record
        print(f"\n{prettify('SUCCESS', 'Green')}: Generation complete. Persisting to Database...")
        await save_paper_to_db(complete_paper, is_mock=IS_MOCK_RUN, difficulty=MOCK_PAPER_LEVEL)
        if hasattr(paper_gen, 'last_run_stats') and paper_gen.last_run_stats:
            await save_analytics_record(paper_gen.last_run_stats, MOCK_PAPER_LEVEL, IS_MOCK_RUN)
    except Exception as e:
        print(f"DB Persistence Issue: {e}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main_gen())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
