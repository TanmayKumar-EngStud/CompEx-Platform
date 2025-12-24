import threading, queue, time, random, sys, os
from deepseek_utils import DeepseekSession
from question_manager import ManageQuestionData
from io_utils import prettify

class ThreadManager:
    """
    Manages threads for generating questions using Deepseek API.
    Since Deepseek has no strict rate limit per key (user instruction), we assume single key usage with multiple threads.
    """
    def __init__(self):
        # Configurable thread count
        self.num_threads = int(os.getenv("GEN_THREADS", "5"))
        self.lock = threading.Lock()
        
    def process_section(self, exam: str, section: str, section_data: dict):
        """
        Process a specific section using worker threads.
        """
        self.work_queue = queue.Queue()
        self.work_report = queue.Queue()
        self.stop_event = threading.Event()
        
        # Populate queue
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
                self.work_queue.put(prompt_details)
        
        # Start worker threads
        threads = []

        for i in range(self.num_threads):
            t = threading.Thread(target=self._worker_action, args=(i,))
            t.start()
            threads.append(t)
        
        # Block until queue is empty
        self.work_queue.join()

        # Stop threads
        self.stop_event.set()
        for t in threads:
            t.join()
            
        if not self.work_queue.empty():
             print(f"\n{prettify('CRITICAL', 'Red', True)}: Work queue not empty after join. This shouldn't happen.")

    def get_work_report(self): 
        report = []
        while not self.work_report.empty():
            report.append(self.work_report.get())
        return report 

    def _worker_action(self, thread_id):
        while not self.stop_event.is_set():
            try:
                # Blocking get with timeout
                prompt_details = self.work_queue.get(block=True, timeout=1)
            except queue.Empty:
                continue 
            
            try:
                # Create a fresh session for THIS question
                # Each question (parent or simple) gets its own conversation history
                session = DeepseekSession(question_type=prompt_details['question-type'])

                question_manager = ManageQuestionData(
                    prompt_details=prompt_details,
                    generator_session=session, # Pass session instead of gemini_generator
                    target_question_type=prompt_details['question-type']
                )
                
                question_data, stats = question_manager.get_question_data()

                self.work_report.put({'data': question_data, 'stats': stats}, block=False)
                self.work_queue.task_done()
                
            except Exception as e:
                import traceback
                print(f"Error in thread {thread_id}: {e}")
                print(traceback.format_exc())
                # Log error
                self.work_report.put({
                    'error': str(e), 
                    'prompt_details': prompt_details, 
                    'stats': {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}
                }, block=False)
                self.work_queue.task_done()