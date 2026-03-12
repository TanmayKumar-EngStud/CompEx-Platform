
import os
import json
import re
import asyncio
import time
import concurrent.futures
from typing import Optional, List, Dict, Any, Tuple

from io_utils import prettify, record, append_record
from db_artilaries import artilaries
from content_generation_manager import manage_generated_content
from analytics_logger import log_analytics
from question_manager import ManageQuestionData
from thread_creator import AsyncManager
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, *args, **kwargs):
        if iterable:
            return iterable
        class MockTqdm:
            def __init__(self, *args, **kwargs): pass
            def update(self, n=1): pass
            def close(self): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return MockTqdm(*args, **kwargs)

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


class GenQ:
    """
    Coordinator class. Iterates through exams/sections and delegates 
    generation to ManageQuestionData + AsyncManager.
    """
    def __init__(self,
                 prompts_dictionary: dict,
                 max_questions: int = 1,
                 context_label: str = "") -> None:
        self.prompts_dictionary = prompts_dictionary
        self.max_questions = max_questions
        self.context_label = context_label
        self.generated_count = 0
        self.last_run_stats = {}

    @staticmethod
    async def _process_section_task(exam: str, section_id: str, section_data: dict, section_name: str, context_label: str = "") -> dict:
        """
        Worker function to process a single section using AsyncManager.
        """
        async_manager = AsyncManager()
        section_start_time = time.time()
        
        # Process prompts in this section
        await async_manager.process_section(exam, section_name, section_data)
        
        # Collect results
        queue_items = async_manager.get_work_report()
        
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
        
        prefix = f"{prettify(context_label, 'Magenta')} " if context_label else ""
        print(f"{prefix}🏁 Finished Section: {prettify(exam, 'Green')} - {prettify(section_name, 'Yellow')} "
              f"({section_stats['questions_generated']} Qs in {section_stats['time_taken']:.2f}s)")

        return {
            'exam': exam,
            'section_id': section_id,
            'section_name': section_name,
            'questions': questions_data,
            'stats': section_stats,
            'errors': error_logs
        }

    async def generate(self) -> dict:
        await artilaries.connect()
        # Fetch question structure mapping once
        global all_question_structure
        mapping = await artilaries.get_question_component_mapping()
        # Ensure we have the list format expected by the rest of the code
        if isinstance(mapping, list):
             all_question_structure = mapping[0]
        else:
             all_question_structure = mapping

        paper_set = {} # {exam: {section_id: {section: name, questions: []}}}
        
        for exam in self.prompts_dictionary:
            paper_set[exam] = {}

        global_stats = {
            'total_api_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_time_seconds': 0,
            'gre_questions': 0,
            'gmat_questions': 0,
            'model_used': os.getenv("MODEL2", "deepseek")
        }
        
        start_time_global = time.time()

        tasks_metadata = [] 
        for exam, sections in self.prompts_dictionary.items():
            for section_id, section_data in sections.items():
                section_name = section_data['section']
                tasks_metadata.append((exam, section_id, section_data, section_name))
        
        print(f"\n{prettify('ASYNC GENERATION STARTED', 'Cyan', True)}")
        print(f"Total Sections to Process: {len(tasks_metadata)}")
        
        # Limit parallel sections
        max_parallel_sections = 10
        semaphore = asyncio.Semaphore(max_parallel_sections)
        
        async def sem_task(t):
            async with semaphore:
                return await self._process_section_task(t[0], t[1], t[2], t[3], self.context_label)

        results = await asyncio.gather(*(sem_task(t) for t in tasks_metadata), return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                print(f"{prettify('CRITICAL ERROR', 'Red')}: Section task failed: {result}")
                continue
                
            exam = result['exam']
            section_id = result['section_id']
            section_name = result['section_name']
            
            paper_set[exam][section_id] = {
                'section': section_name,
                'questions': result['questions']
            }
            
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

        global_stats['total_time_seconds'] = time.time() - start_time_global
        
        print("\n" + "="*30)
        print("Paper generation completed!")
        
        for exam, paper_data in paper_set.items():
            paper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper')
            os.makedirs(paper_path, exist_ok=True)
            paper_file_path = os.path.join(paper_path, f'{exam}.json')
            
            with open(paper_file_path, 'w', encoding='utf-8') as f:
                json.dump(paper_data, f, indent=2, ensure_ascii=False)
            
            print(f"{exam}: log_json_files/paper/{exam}.json")
        
        print(f"Total Time taken: {global_stats['total_time_seconds']:.2f}s")
        print(f"Total Questions: {global_stats['gre_questions'] + global_stats['gmat_questions']}")
        print("="*30 + "\n")

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
        await artilaries.disconnect()
        return paper_set