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
        self.stop_event = threading.Event() # Event to signal worker threads to stop

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
        
        # Block until all items in the work_queue have been processed.
        # This includes any items that are re-queued due to failure, as task_done() is only called on success or final failure,
        # or in our case, if we re-queue, we call task_done() on the *failed* item, but the new item keeps the count up.
        # Wait... if we re-queue:
        # 1. get() -> unfinished_tasks-- (Wait, get doesn't decr. task_done decr.)
        # 2. put() -> unfinished_tasks++
        # 3. task_done() on failed item -> unfinished_tasks--
        # Net change: 0. So logic holds.
        self.work_queue.join()

        # Signal all threads to stop
        self.stop_event.set()
        
        # Wait for all threads to terminate gracefully
        for t in threads:
            t.join()
        
        # Check if work queue is not empty (defensive check)
        if not self.work_queue.empty():
            print(f"\n{prettify('CRITICAL', 'Red', True)}: Work queue not empty after join. This shouldn't happen.")
            # sys.exit(1) # Don't exit, just warn.

    def get_work_report(self): 
        report = []
        while not self.work_report.empty():
            report.append(self.work_report.get())
        return report 

    def _worker_action(self, api_key):
        while not self.stop_event.is_set():
            # Check if this key is still valid (it might have been removed by another thread?? 
            # No, if I am running with it, I am the owner of this key instance. 
            # But if I fail, I remove myself from the global pool.)
            
            try:
                # Blocking get with timeout allows checking stop_event periodically
                prompt_details = self.work_queue.get(block=True, timeout=1)
            except queue.Empty:
                continue # Loop back to check stop_event
            
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
                    break # Terminate this thread as key is dead
                
                print(f"Error in thread with key {api_key}: {e}")
                print(f"Error in thread with key {api_key}: {e}")
                import traceback
                # traceback.print_exc()
                self.work_report.put({'error': str(e), 'prompt_details': prompt_details, 'stats': {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}}, block=False)
                self.work_queue.task_done()