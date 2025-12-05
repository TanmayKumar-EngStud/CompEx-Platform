"""
Here we will get complete prompt dictionary, we will traverse from every question prompt, generate their respective question components as per given in `question_component_types.json`.
"""

import os
import json
import re
from typing import Optional, List, Dict, Any

from io_utils import get_json, prettify, get_Component_Template, record, append_record
from api_utils import get_gemini_generator
from content_generation_manager import manage_generated_content
from analytics_logger import log_analytics
import time
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, *args, **kwargs):
        if iterable:
            return iterable
        # If used as a context manager or manual update
        class MockTqdm:
            def __init__(self, *args, **kwargs): pass
            def update(self, n=1): pass
            def close(self): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return MockTqdm(*args, **kwargs)

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



from question_manager import ManageQuestionData
from thread_creator import SectionThread

class GenQ:
    """
    Coordinator class. Iterates through exams/sections and delegates 
    generation to ManageQuestionData.
    """
    def __init__(self,
                 prompts_dictionary: dict,
                 max_questions: int = 1) -> None:
        self.prompts_dictionary = prompts_dictionary
        self.max_questions = max_questions
        self.generated_count = 0

    def generate(self) -> dict:
        paper_set = {}
        
        # Global stats for analytics
        global_stats = {
            'total_api_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_time_seconds': 0,
            'gre_questions': 0,
            'gmat_questions': 0,
            'model_used': os.getenv("MODEL2", "gemini-2.5-flash") # Default or from env
        }
        
        start_time_global = time.time()

        for exam, sections in self.prompts_dictionary.items():
            self.generated_count = 0
            log_generation_stage(
                exam, detail=prettify('Initializing question generation', 'Magenta')
            )
            paper = {}
            
            print(f"\nReport:")
            print(f"Current Exam: {prettify(exam, 'Green')}")

            for section_id, section_data in sections.items():
                section = section_data['section']
                print(f"Section: {prettify(section, 'Yellow')}")
                
                paper[section_id] = {
                    'section': section,
                    'questions': []
                }
                
                # Stats for this section
                section_stats = {
                    'questions_generated': 0,
                    'time_taken': 0,
                    'api_calls': 0,
                    'input_tokens': 0,
                    'output_tokens': 0
                }
                
                section_start_time = time.time()
                
                # Use SectionThread to process all questions in this section concurrently
                section_thread = SectionThread(exam, section, section_data)
                
                # Get raw items from queue (now dicts with data and stats)
                queue_items = section_thread.get_work_report()
                
                # Process items with progress bar
                questions_data = []
                
                # Calculate total expected items (approximate based on queue size)
                total_items = len(queue_items)
                
                with tqdm(total=total_items, desc=f"Generating {section}", unit="q") as pbar:
                    for item in queue_items:
                        if 'error' in item:
                            print(f"\nError in generation: {item['error']}")
                            # Still count stats if available (e.g. failed after some calls)
                            if 'stats' in item:
                                section_stats['api_calls'] += item['stats'].get('api_calls', 0)
                                section_stats['input_tokens'] += item['stats'].get('input_tokens', 0)
                                section_stats['output_tokens'] += item['stats'].get('output_tokens', 0)
                        else:
                            question_data = item['data']
                            stats = item['stats']
                            
                            questions_data.append(question_data)
                            
                            # Aggregate stats
                            # Count parent + children
                            child_count = len(question_data.get('child-questions', []))
                            # User said: "simple questions + child questions (don't count parent question 😅)"
                            # If it has children, it's a parent. So count children.
                            # If it has no children, it's a simple question. Count 1.
                            if child_count > 0:
                                section_stats['questions_generated'] += child_count
                            else:
                                section_stats['questions_generated'] += 1
                                
                            section_stats['api_calls'] += stats['api_calls']
                            section_stats['input_tokens'] += stats['input_tokens']
                            section_stats['output_tokens'] += stats['output_tokens']
                        
                        pbar.update(1)
                
                section_end_time = time.time()
                section_stats['time_taken'] = section_end_time - section_start_time
                
                paper[section_id]['questions'].extend(questions_data)
                
                # Print Section Report
                print(f"{prettify(section, 'Green')} Done ✅")
                print(f"- Total number of questions generated: {section_stats['questions_generated']}")
                print(f"- time taken: {section_stats['time_taken']:.2f}s")
                print(f"- API calls: {section_stats['api_calls']}")
                print(f"- input token: {section_stats['input_tokens']}")
                print(f"- output token: {section_stats['output_tokens']}")
                
                # Update global stats
                global_stats['total_api_calls'] += section_stats['api_calls']
                global_stats['total_input_tokens'] += section_stats['input_tokens']
                global_stats['total_output_tokens'] += section_stats['output_tokens']
                
                if exam == 'GRE':
                    global_stats['gre_questions'] += section_stats['questions_generated']
                elif exam == 'GMAT':
                    global_stats['gmat_questions'] += section_stats['questions_generated']

                # After processing a section, check if the target limit is reached
                # (Logic slightly adjusted as we process whole sections now)
                self.generated_count += len(questions_data)
                if self.generated_count >= self.max_questions:
                    print(f"{prettify('Limit Reached', 'Yellow')}: {self.max_questions} questions generated for {exam}")
                    # break # Don't break section loop, just stop exam loop if needed? 
                    # Actually original logic broke inner loop.
            
            paper_set[exam] = paper
            
            print(f"{prettify(exam, 'Green')} paper is being generated ✅")
            
            # Save paper to log_json_files/paper/{exam}.json
            paper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper')
            os.makedirs(paper_path, exist_ok=True)
            paper_file_path = os.path.join(paper_path, f'{exam}.json')
            with open(paper_file_path, 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)
                
        global_stats['total_time_seconds'] = time.time() - start_time_global
        
        # Final Report
        print("\n" + "="*30)
        print("Paper generation completed!")
        for exam in paper_set:
             print(f"{exam}: log_json_files/paper/{exam}.json")
        
        print(f"Model used: {global_stats['model_used']}")
        print(f"Total Input tokens: {global_stats['total_input_tokens']}")
        print(f"Total Output tokens: {global_stats['total_output_tokens']}")
        print(f"Total Time taken: {global_stats['total_time_seconds']:.2f}s")
        print(f"Total API calls: {global_stats['total_api_calls']}")
        print("="*30 + "\n")

        # Log to CSV
        log_analytics(
            model_used=global_stats['model_used'],
            total_api_calls=global_stats['total_api_calls'],
            total_input_tokens=global_stats['total_input_tokens'],
            total_output_tokens=global_stats['total_output_tokens'],
            total_time_seconds=global_stats['total_time_seconds'],
            gre_questions=global_stats['gre_questions'],
            gmat_questions=global_stats['gmat_questions']
        )

        return paper_set