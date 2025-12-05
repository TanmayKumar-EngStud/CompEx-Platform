import threading, queue, time, random, sys
from api_utils import get_gemini_generator
from question_manager import ManageQuestionData
from io_utils import prettify

class ThreadManager:
    """
    Manages API keys and threads across multiple sections to ensure persistent state.
    """
    def __init__(self):
        # Initialize with all keys available
        self.api_keys = [i for i in range(13)]
        self.lock = threading.Lock()
        
    def process_section(self, exam: str, section: str, section_data: dict):
        """
        Process a specific section using the currently available API keys.
        """
        self.work_queue = queue.Queue()
        self.work_report = queue.Queue()

        for qt, qt_info in section_data.items():
            if qt == 'section':
                continue
            
            for prompt_data in qt_info['prompts']:
                prompt_details = {
                    'type': qt_info['type'],
                    'exam': exam,
                    'section': section,
                    'question-type': qt,
                    'option': prompt_data.get('option'),
                    'prompt': prompt_data.get('prompt'),
                    'child-prompt': prompt_data.get('child-prompt'),
                    'metadata-type': prompt_data.get('metadata-type')
                }
                self.work_queue.put(prompt_details)
        
        # Check if we have any valid keys left before starting
        with self.lock:
             current_keys = list(self.api_keys) # copy

        if not current_keys:
             print(f"\n{prettify('CRITICAL', 'Red', True)}: No API keys available at start of section. Terminating.")
             sys.exit(1)

        # Creating the threads with current available keys
        threads = []
        for api_key in current_keys:
            t = threading.Thread(target = self._worker_action, args = (api_key,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        # Check if work queue is not empty after all threads are done
        # This could happen if all keys got blacklisted DURING this section
        if not self.work_queue.empty():
            print(f"\n{prettify('CRITICAL', 'Red', True)}: All API keys exhausted. Terminating program.")
            sys.exit(1)

    def get_work_report(self): 
        report = []
        while not self.work_report.empty():
            report.append(self.work_report.get())
        return report 

    def _worker_action(self, api_key):
        while True:
            # Check if this key is still valid (it might have been removed by another thread?? 
            # No, if I am running with it, I am the owner of this key instance. 
            # But if I fail, I remove myself from the global pool.)
            
            try:
                # Non-blocking get to drain queue if threads are running
                prompt_details = self.work_queue.get(block = False)
            except queue.Empty:
                print(f"API Key: {api_key} is done")
                break
            
            try:
                # We simply use the key we were assigned
                gemini_generator = get_gemini_generator(api_key_index = api_key, question_type = prompt_details['question-type'])

                question_manager = ManageQuestionData(
                    prompt_details = prompt_details,
                    gemini_generator = gemini_generator,
                    target_question_type = prompt_details['question-type']
                )
                question_data, stats = question_manager.get_question_data()

                self.work_report.put({'data': question_data, 'stats': stats}, block = False)
                self.work_queue.task_done()
            except Exception as e:
                error_msg = str(e)
                if "Request Per Day limit exceeded" in error_msg:
                    print(f"\n{prettify('API_KEY' + str(api_key), 'Red', True)}: {prettify('[BLACKLISTED]', 'Red', True)}")
                    
                    # Remove from global persistent list
                    with self.lock:
                        if api_key in self.api_keys:
                            self.api_keys.remove(api_key)
                    
                    # Re-queue the work so another thread can pick it up
                    self.work_queue.put(prompt_details)
                    self.work_queue.task_done() 
                    break 
                
                print(f"Error in thread with key {api_key}: {e}")
                import traceback
                traceback.print_exc()
                self.work_report.put({'error': str(e), 'prompt_details': prompt_details, 'stats': {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}}, block=False)
                self.work_queue.task_done()