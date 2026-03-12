import asyncio
import time
import random
import sys
import os
from deepseek_utils import DeepseekSession
from question_manager import ManageQuestionData
from io_utils import prettify

class AsyncManager:
    """
    Manages concurrent generation of questions using asyncio.
    Replaces the older ThreadManager to support the new async/await pipeline.
    """
    def __init__(self):
        # Configurable concurrency limit
        self.max_concurrent_tasks = int(os.getenv("GEN_THREADS", "5"))
        self.work_report = []
        
    async def process_section(self, exam: str, section: str, section_data: dict):
        """
        Process a specific section concurrently.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        tasks = []
        
        # Populate tasks
        for qt, qt_info in section_data.items():
            if qt == 'section':
                continue
            
            for prompt_data in qt_info['prompts']:
                prompt_details = {
                    'type': qt_info['type'],
                    'exam': exam,
                    'section': section,
                    'question-type': qt,
                    **prompt_data
                }
                tasks.append(self._generate_question_task(prompt_details, semaphore))
        
        # Run all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)

    async def _generate_question_task(self, prompt_details: dict, semaphore: asyncio.Semaphore):
        """
        Wraps question generation with a semaphore for concurrency control.
        """
        async with semaphore:
            try:
                # Create a fresh session for THIS question
                session = DeepseekSession(question_type=prompt_details['question-type'])

                question_manager = ManageQuestionData(
                    prompt_details=prompt_details,
                    generator_session=session,
                    target_question_type=prompt_details['question-type']
                )
                
                question_data, stats = await question_manager.get_question_data()

                self.work_report.append({'data': question_data, 'stats': stats})
                
            except Exception as e:
                import traceback
                print(f"Error generating question: {e}")
                print(traceback.format_exc())
                # Log error
                self.work_report.append({
                    'error': str(e), 
                    'prompt_details': prompt_details, 
                    'stats': {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
                })

    def get_work_report(self): 
        return self.work_report