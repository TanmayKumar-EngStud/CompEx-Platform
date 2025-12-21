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
from question_manager import ManageQuestionData
from thread_creator import ThreadManager # Updated import
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

import concurrent.futures

class GenQ:
    """
    Coordinator class. Iterates through exams/sections and delegates 
    generation to ManageQuestionData + ThreadManager.
    """
    def __init__(self,
                 prompts_dictionary: dict,
                 max_questions: int = 1) -> None:
        self.prompts_dictionary = prompts_dictionary
        self.max_questions = max_questions
        self.generated_count = 0
        self.last_run_stats = {}

    @staticmethod
    def _process_section_task(exam: str, section_id: str, section_data: dict, section_name: str) -> dict:
        """
        Worker function to process a single section including thread management and stats.
        Returns a dict with results and stats.
        """

        
        # Instantiate a FRESH ThreadManager for this section (This manager spawns its own internal threads)
        thread_manager = ThreadManager()
        
        section_start_time = time.time()
        
        # Process prompts in this section (This blocks until internal threads are done)
        thread_manager.process_section(exam, section_name, section_data)
        
        # Collect results
        queue_items = thread_manager.get_work_report()
        
        questions_data = []
        section_stats = {
            'questions_generated': 0,
            'time_taken': 0,
            'api_calls': 0,
            'input_tokens': 0,
            'output_tokens': 0
        }
        
        error_logs = []

        for item in queue_items:
            if 'error' in item:
                error_logs.append(item['error'])
                if 'stats' in item:
                    section_stats['api_calls'] += item['stats'].get('api_calls', 0)
                    section_stats['input_tokens'] += item['stats'].get('input_tokens', 0)
                    section_stats['output_tokens'] += item['stats'].get('output_tokens', 0)
            else:
                question_data = item['data']
                stats = item['stats']
                questions_data.append(question_data)
                
                # Count stats
                child_count = len(question_data.get('child-questions', []))
                if child_count > 0:
                    section_stats['questions_generated'] += child_count
                else:
                    section_stats['questions_generated'] += 1
                    
                section_stats['api_calls'] += stats['api_calls']
                section_stats['input_tokens'] += stats['input_tokens']
                section_stats['output_tokens'] += stats['output_tokens']
        
        section_end_time = time.time()
        section_stats['time_taken'] = section_end_time - section_start_time
        
        print(f"🏁 Finished Section: {prettify(exam, 'Green')} - {prettify(section_name, 'Yellow')} "
              f"({section_stats['questions_generated']} Qs in {section_stats['time_taken']:.2f}s)")

        return {
            'exam': exam,
            'section_id': section_id,
            'section_name': section_name,
            'questions': questions_data,
            'stats': section_stats,
            'errors': error_logs
        }

    def generate(self) -> dict:
        paper_set = {} # {exam: {section_id: {section: name, questions: []}}}
        
        # Initialize structure
        for exam in self.prompts_dictionary:
            paper_set[exam] = {}

        global_stats = {
            'total_api_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_time_seconds': 0,
            'gre_questions': 0,
            'gmat_questions': 0,
            'model_used': os.getenv("MODEL2", "deepseek") # Default
        }
        
        start_time_global = time.time()

        # 1. Collect all Tasks
        tasks = [] # (exam, section_id, section_data, section_name)
        
        for exam, sections in self.prompts_dictionary.items():
            for section_id, section_data in sections.items():
                section_name = section_data['section']
                tasks.append((exam, section_id, section_data, section_name))
        
        print(f"\n{prettify('PARALLEL GENERATION STARTED', 'Cyan', True)}")
        print(f"Total Sections to Process: {len(tasks)}")
        
        # 2. Execute Parallel Tasks
        # We use a ThreadPoolExecutor. 
        # Note: ThreadManager inside each task ALSO spawns threads.
        # This is nested threading. Since simple IO blocking, it's fine.
        # Max Workers = Max parallel sections.
        max_parallel_sections = 21 # Scaled up as per user request
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_sections) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._process_section_task, t[0], t[1], t[2], t[3]): t 
                for t in tasks
            }
            
            for future in concurrent.futures.as_completed(future_to_task):
                task_info = future_to_task[future]
                try:
                    result = future.result()
                    
                    # 3. Aggregate Results
                    exam = result['exam']
                    section_id = result['section_id']
                    section_name = result['section_name']
                    
                    # Store in paper_set
                    paper_set[exam][section_id] = {
                        'section': section_name,
                        'questions': result['questions']
                    }
                    
                    # Aggregate Stats
                    s_stats = result['stats']
                    global_stats['total_api_calls'] += s_stats['api_calls']
                    global_stats['total_input_tokens'] += s_stats['input_tokens']
                    global_stats['total_output_tokens'] += s_stats['output_tokens']
                    
                    if exam == 'GRE':
                        global_stats['gre_questions'] += s_stats['questions_generated']
                    elif exam == 'GMAT':
                        global_stats['gmat_questions'] += s_stats['questions_generated']
                        
                    if result['errors']:
                        print(f"⚠️ Errors in {section_name}: {len(result['errors'])}")
                        
                except Exception as exc:
                    print(f"{prettify('CRITICAL ERROR', 'Red')}: Task {task_info} generated an exception: {exc}")

        global_stats['total_time_seconds'] = time.time() - start_time_global
        
        # 4. Final Output & Saving
        print("\n" + "="*30)
        print("Paper generation completed!")
        
        for exam, paper_data in paper_set.items():
            # Save paper
            paper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper')
            os.makedirs(paper_path, exist_ok=True)
            paper_file_path = os.path.join(paper_path, f'{exam}.json')
            
            # Ensure serialization safe
            with open(paper_file_path, 'w', encoding='utf-8') as f:
                json.dump(paper_data, f, indent=2, ensure_ascii=False)
            
            print(f"{exam}: log_json_files/paper/{exam}.json")
        
        print(f"Total Time taken: {global_stats['total_time_seconds']:.2f}s")
        print(f"Total Questions: {global_stats['gre_questions'] + global_stats['gmat_questions']}")
        print("="*30 + "\n")

        # Log to CSV
        log_analytics(
            model_used=global_stats['model_used'],
            total_api_calls=global_stats['total_api_calls'],
            total_input_tokens=global_stats['total_input_tokens'],
            total_output_tokens=global_stats['total_output_tokens'],
            total_time_seconds=global_stats['total_time_seconds'],
            gmat_questions=global_stats['gmat_questions'],
            gre_questions=global_stats['gre_questions']
        )
        self.last_run_stats = global_stats
        return paper_set