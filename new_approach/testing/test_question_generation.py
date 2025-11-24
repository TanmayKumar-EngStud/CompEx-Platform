import os
import sys
import json
import random
from dotenv import load_dotenv

# Add qGen-new directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qGen-new'))

from generator import GenQ
from prepare_prompts import PromptPrep
from io_utils import get_json, prettify

def test_question_generation(target_style=None):
    # Load env
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path)

    # Load definitions
    exam_definition, qt_info = get_json('exam_definition', 'question_type_info')
    
    available_styles = list(qt_info.keys())
    
    if not target_style:
        print("\nAvailable Question Styles:")
        for i, style in enumerate(available_styles):
            print(f"{i+1}. {style}")
        
        try:
            choice = int(input("\nSelect a Question Style (number): "))
            target_style = available_styles[choice-1]
        except (ValueError, IndexError):
            print("Invalid selection. Exiting.")
            return

    print(f"\n🧪 Testing generation for: {prettify(target_style, 'Cyan')}")

    # Construct a minimal prompts_dictionary for this style
    # We need to find an exam/section that contains this style
    found = False
    target_exam = ""
    target_section = ""
    target_section_id = ""

    for exam, sections in exam_definition.items():
        for sec_id, sec_data in sections.items():
            if target_style in sec_data['question types']:
                target_exam = exam
                target_section = sec_data['name']
                target_section_id = sec_id
                found = True
                break
        if found: break
    
    if not found:
        print(f"❌ Could not find any exam/section containing {target_style}")
        return

    print(f"   Using Exam: {target_exam}, Section: {target_section}")

    # Generate a single prompt for this style
    print("   Generating prompt...")
    question_type_info = qt_info[target_style]
    
    # Mock difficulty
    difficulty = 3 
    nomenclature = question_type_info["nomenclature"]
    
    # Use PromptPrep to generate a valid prompt string
    prompt = PromptPrep._nomenclature_to_prompt_mapping(nomenclature, target_style, difficulty)
    
    prompt_buffer = {
        'prompt': prompt,
    }

    # Handle Options
    if question_type_info.get('options'):
        option = question_type_info['options']
        if isinstance(option, dict):
            option = random.choices(list(option.keys()), weights=list(option.values()))[0]
        prompt_buffer['option'] = option

    # Handle Metadata
    if question_type_info.get('has-metadata'):
        count = question_type_info.get('meta-count', 1)
        metadata_options_dict = PromptPrep._selective_metadata_info(target_style)
        metadata_buffer = {}
        for _ in range(count):
            if not metadata_options_dict:
                 print(f"⚠️ No metadata options found for {target_style}")
                 break
            category = random.choice(list(metadata_options_dict.keys()))
            if category not in metadata_buffer:
                metadata_buffer[category] = []
            metadata_buffer[category].append(random.choice(metadata_options_dict[category]))
        prompt_buffer['metadata-type'] = metadata_buffer

    # Handle Child Questions (if Parent)
    if question_type_info.get('child-question'):
        prompt_buffer['child-prompt'] = []
        # Create 3 child prompts for testing
        child_info = question_type_info['child-question']
        child_diff = 3
        
        for _ in range(3):
            child_prompt_str = PromptPrep._nomenclature_to_prompt_mapping(
                child_info['nomenclature'], target_style, child_diff)
            
            child_opt = child_info['options']
            if isinstance(child_opt, dict):
                 child_opt = random.choices(list(child_opt.keys()), weights=list(child_opt.values()))[0]

            child_prompt_data = {
                'prompt': child_prompt_str,
                'option': child_opt
            }
            if child_info.get('question-type'):
                child_prompt_data['question-type'] = child_info['question-type']
            
            prompt_buffer['child-prompt'].append(child_prompt_data)

    # Construct the dictionary
    prompts_dictionary = {
        target_exam: {
            target_section_id: {
                'section': target_section,
                target_style: {
                    'type': question_type_info['type'],
                    'prompts': [prompt_buffer]
                }
            }
        }
    }

    # Initialize GenQ
    print("   Initializing GenQ...")
    gen = GenQ(prompts_dictionary, target_question_type=target_style, max_questions=1)
    
    # Run Generation
    print("   Running generation (this calls the API)...")
    try:
        paper_set = gen.generate()
        
        # Verify output
        questions = paper_set[target_exam][target_section_id]['questions']
        if questions and len(questions) > 0:
            print(f"\n✅ Successfully generated {len(questions)} question(s)!")
            print("   Output Preview:")
            print(json.dumps(questions[0], indent=2))
        else:
            print("\n❌ Generation completed but no questions were returned.")
            
    except Exception as e:
        print(f"\n❌ Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    style = sys.argv[1] if len(sys.argv) > 1 else None
    test_question_generation(style)
