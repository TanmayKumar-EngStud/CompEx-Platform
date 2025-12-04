import threading, queue, time, random
from api_utils import get_gemini_generator
from question_manager import ManageQuestionData

class SectionThread:
    def __init__(self, exam, section,section_data: dict):
        self.work_queue = queue.Queue()

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
        self.work_report = queue.Queue()
        self.api_keys = [i for i in range(10)]

        # Creating the threads:
        threads = []
        for i, api_key in enumerate(self.api_keys):
            t = threading.Thread(target = self._worker_action, args = (i, api_key))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
    def get_work_report(self): 
        report = []
        while not self.work_report.empty():
            report.append(self.work_report.get())
        return report 

    def _worker_action(self, thread_id, api_key):
        while True:
            try:
                prompt_details = self.work_queue.get(block = False)
            except queue.Empty:
                print(f"API Key: {api_key} is done")
                break
            try:
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
                print(f"Error in thread {thread_id} with key {api_key}: {e}")
                import traceback
                traceback.print_exc()
                self.work_report.put({'error': str(e), 'prompt_details': prompt_details, 'stats': {'input_tokens': 0, 'output_tokens': 0, 'api_calls': 0}}, block=False)
                self.work_queue.task_done()