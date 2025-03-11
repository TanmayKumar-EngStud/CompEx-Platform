import threading
import time
import random
import queue as q

class Task: # question
   """Every task is a single question that is going to be generated

   It will have some global values such as startTimer, requestCounter which will be passed by the previous thread
   """
   def __init__(self, api_IDX, thread_id, startTimer=None, requestCounter = 0):
      self.api_IDX = api_IDX
      self.requestCounter = requestCounter
      self.startTimer = startTimer
      self.thread_id = thread_id
      if not startTimer:
         self.startTimer = time.time()
   
   def generate_question(self, prompt):
      """Here question will generate based on the given prompt user can have multiple arguments as per the scenario which is followed for section wise question generation as of now.
      """
      self.startTimer, self.requestCounter, questionContent = self.____hiddenQuestionGenerator(self.thread_id, self.startTimer, self.requestCounter, self.api_IDX, prompt)
      return self.startTimer, self.requestCounter, questionContent
   
   def ____hiddenQuestionGenerator(thread_id, startTimer, requestCounter, api_IDX, prompt):
      """This one is the hidden function that will generate the questions"""
      num_counts = random.randint(8, 12)
      presentTime = time.time()
      if(num_counts + requestCounter >= 10):
         elapsed = presentTime - startTimer
         if elapsed < 3:
            wait_time = 60 - elapsed + 0.5 # small buffer
            time.sleep(2)  
            print(f"Sleeping for 2 seconds for API_{api_IDX}")
         startTimer = time.time()
         requestCounter = 1
      response = f"Prompt: {prompt}"
      ret =  {
         "API_KEY": f"API_KEY_{api_IDX}",
         "thread_id": f"thread_{thread_id}",
         "response": response,
      }
      time.sleep(1)
      return startTimer, requestCounter, ret
   

def worker(thread_id, task_queue, api_IDX, startTimer, requestCounter):  
   """From the Task queue a task class will be initialized and will be generated"""
   if not task_queue.EMPTY:
      task_id = task_queue.get(timeout = 0.1)
      prompt = f"task:- {task_id}"

      t = Task(api_IDX=api_IDX, thread_id=thread_id, startTimer=startTimer, requestCounter=requestCounter)
      return startTimer, requestCounter, t.generate_question(prompt=prompt)
   else:
      return startTimer, requestCounter, "Empty"

def main(tasks, num_threads, api_keys):
   task_queue = q.Queue()
   for task in tasks:
      task_queue.put(task)
   
   threads = []
   for i in range(num_threads):
      thread = threading.Thread()