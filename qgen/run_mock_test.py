"""
run_mock_test.py — generates GRE + GMAT mock papers at a given difficulty,
saves date-stamped JSON files, and registers them in the Neon database.
"""
import os, sys, json, random, asyncio, argparse
from datetime import datetime
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, '.env'))

from io_utils import prettify
from difficulty_pool import get_difficulty_pool, initialize_difficulty_pool
from question_manager import initialize_question_manager
from prepare_prompts import PromptPrep, load_configs
from generator import GenQ
from db_integration import save_paper_to_db

async def run_mock_generation(difficulty: int):
    print(f"\n{'='*60}")
    print(f"  CompEx Mock Paper Generator")
    print(f"  Difficulty: {difficulty}/5  |  Mode: MOCK  |  Exams: GRE + GMAT")
    print(f"{'='*60}\n")

    print(f"{prettify('INIT', 'Yellow')}: Loading exam configs...")
    await load_configs()
    await initialize_difficulty_pool()
    await initialize_question_manager()

    # Import globals populated by load_configs()
    from prepare_prompts import exam_definition, qt_info
    if not exam_definition:
        print(f"{prettify('ERROR', 'Red')}: exam_definition is empty")
        sys.exit(1)

    print(f"{prettify('EXAMS', 'Cyan')}: Found: {list(exam_definition.keys())}")

    prompts_dictionary = {}
    for exam, sections in sorted(exam_definition.items(), key=lambda x: x[0], reverse=True):
        prompts_dictionary[exam] = {}
        for section_number, section in sections.items():
            section_name = section['name']
            n_items = section['total']
            difficulty_list = get_difficulty_pool(exam, section_name, n_items + 5, difficulty)

            # Question types live at the TOP LEVEL of the section dict (alongside 'section')
            prompts_dictionary[exam][section_number] = {
                'section': section_name
            }

            for question_type in section['question types']:
                # Get per-type info (needed for 'type', 'has-metadata', 'options', 'nomenclature')
                question_type_info = PromptPrep._must_get(qt_info, question_type, 'question_type_info.json')
                count_needed = section[question_type]

                prompts_dictionary[exam][section_number][question_type] = {
                    "has-metadata": question_type_info.get('has-metadata', False),
                    'type': question_type_info.get('type', 'simple'),
                    'prompts': []
                }

                prompt_count = 0
                while prompt_count < count_needed:
                    current_difficulty = difficulty_list.pop() if difficulty_list else difficulty
                    nomenclature = question_type_info.get("nomenclature", "")
                    try:
                        prompt, instruction_str, parsed_tags = await PromptPrep._nomenclature_to_prompt_mapping(
                            nomenclature, question_type, current_difficulty, exam_name=exam)
                    except ValueError as e:
                        print(f"\n{prettify('FATAL', 'Red')}: {e}")
                        sys.exit(1)

                    prompt_buffer = {
                        'prompt': prompt,
                        'instruction_str': instruction_str,
                        'parsed_tags': parsed_tags,
                        'difficulty': current_difficulty,
                    }

                    if question_type_info.get('options'):
                        options = question_type_info['options']
                        if isinstance(options, dict):
                            option = random.choices(list(options.keys()), weights=list(options.values()))[0]
                        else:
                            option = random.choice(options) if isinstance(options, list) else options
                        prompt_buffer['option'] = option

                    if question_type_info.get('has-metadata'):
                        metadata_options = await PromptPrep._selective_metadata_info(question_type)
                        metadata_buffer = {}
                        for cat, opts in metadata_options.items():
                            metadata_buffer[cat] = [random.choice(opts)]
                        prompt_buffer['metadata-type'] = metadata_buffer

                    # Build child prompts for parent question types (RC, Problem Solving Meta, MSR)
                    child_info = question_type_info.get('child-question')
                    if child_info and question_type_info.get('type') == 'parent':
                        child_nomenclature = child_info.get('nomenclature', '')
                        # MSR children are a distinct question type; others inherit the parent type
                        child_qt = child_info.get('question-type', question_type)
                        child_options = child_info.get('options', {'single': 1})

                        # Determine how many children this parent needs
                        try:
                            child_count = await PromptPrep._get_child_count(
                                child_nomenclature, child_qt, prompt_buffer['prompt'], child_info)
                        except Exception:
                            child_count = 2  # safe fallback

                        child_prompts = []
                        for _ in range(child_count):
                            # Pick option type for this child
                            if isinstance(child_options, dict):
                                child_option = random.choices(
                                    list(child_options.keys()),
                                    weights=list(child_options.values()))[0]
                            elif isinstance(child_options, list):
                                child_option = random.choice(child_options)
                            else:
                                child_option = child_options

                            try:
                                c_prompt, c_instruction_str, c_parsed_tags = await PromptPrep._nomenclature_to_prompt_mapping(
                                    child_nomenclature, child_qt, current_difficulty, exam_name=exam)
                            except ValueError as e:
                                print(f"\n{prettify('WARN', 'Yellow')}: child prompt build failed for {child_qt}: {e}")
                                continue

                            child_prompts.append({
                                'question-type': child_qt,
                                'option': child_option,
                                'prompt': c_prompt,
                                'instruction_str': c_instruction_str,
                                'parsed_tags': c_parsed_tags,
                                'difficulty': current_difficulty,
                            })

                        prompt_buffer['child-prompt'] = child_prompts

                    prompts_dictionary[exam][section_number][question_type]['prompts'].append(prompt_buffer)
                    prompt_count += 1

    log_dir = os.path.join(project_root, 'log_json_files')
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, 'mock_test_prompts.json'), 'w') as f:
        json.dump(prompts_dictionary, f, indent=2)

    print(f"\n{prettify('GEN', 'Green')}: Starting question generation...")
    paper_gen = GenQ(prompts_dictionary)
    complete_paper = await paper_gen.generate()

    # Save date-stamped JSON files
    date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    paper_dir = os.path.join(log_dir, 'paper')
    os.makedirs(paper_dir, exist_ok=True)
    for exam_name in ['GRE', 'GMAT']:
        if exam_name in complete_paper:
            json_path = os.path.join(paper_dir, f'{exam_name}_{date_str}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({exam_name: complete_paper[exam_name]}, f, indent=2, ensure_ascii=False)
            print(f"{prettify('SAVED', 'Green')}: {json_path}")

    # Save to Neon DB
    print(f"\n{prettify('DB', 'Yellow')}: Saving to Neon DB (difficulty={difficulty}, is_mock=True)...")
    await save_paper_to_db(complete_paper, is_mock=True, difficulty=difficulty)
    print(f"\n{prettify('DONE', 'Green', True)}: Mock paper generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--difficulty", type=int, default=5, choices=range(1, 6))
    args = parser.parse_args()
    try:
        asyncio.run(run_mock_generation(args.difficulty))
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
