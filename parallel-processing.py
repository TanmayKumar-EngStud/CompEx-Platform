"""
Thread pool + shared task queue
Work Distribution mechanism

1. Fixed number of thread initialization.
2. creation of shared task_queue
3. Initial assignment of x tasks to x threads
4. when any thread completes the task it gets the next task.
5. this continues till the task is completed.
"""
import os
os.system('clear')
import threading, time, queue
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Any

class APIThreadPoolManager:
   """
   A thread pool manager designed for executing API tasks with shared global variable state
   """
   def __init__(self, num_threads: int):
      """
      Initialize the API thread pool manager.

      Args:
         num_threads: Number of worker threads (API keys) to use
      """
      self.num_threads = num_threads
      self.task_queue = queue.Queue()
      self.lock = threading.Lock()

      self.global_state = {
         "start_time": time.time(),
         "request_count": 0
      }

   def add_tasks(self, tasks: List[Callable]):
      """
      Add tasks to the queue.

      Args:
         tasks: List of task functions to be executed
      """
      for task in tasks:
         self.task_queue.put(task)
      return
   
   def worker(self):
      """
      Worker function that processes the tasks form the queue.
      Each worker represents a thread with access to one API key.
      """
      while not self.task_queue.empty():
         try:
            task = self.task_queue.get(block= False)
            # Execute the task with access to shared global state
            task(self.global_state, self.lock)

            # Mark task as done
            self.task_queue.task_done()
         except queue.Empty:
            break
      return
   
   def execute_all(self):
      """
      Execute all tasks using the thread pool.
      """
      # Create and start the thread pool. 
      with ThreadPoolExecutor(max_workers= self.num_threads) as executor:
         futures = [executor.submit(self.worker) for _ in range(self.num_threads)]
         # wait for all task to complete.
         for future in futures:
            future.result()
   # Return the final state after all tasks are completed
      return self.global_state
   
def api_task(global_state, lock):
   """
   Example API task that increments request count and uses the API key.

   Args:
      global_state: Dictionary containing shared global variables
      lock: Threading lock for safe access to shared variables
   """

   time.sleep(5)

   with lock:
      global_state["request_count"] += 1
      elapsed_time = time.time() - global_state["start_time"]

      # For demonstration, print the current state
      print(f"Task executed. Total requests: {global_state['request_count']},",
            f"Time elapsed: {elapsed_time:.2f}s, ",
            f"Thread: {threading.current_thread().name}")
      
def main():
   num_keys = 3
   num_tasks = 10

   manager = APIThreadPoolManager(num_threads= num_keys)

   # creation of tasks 
   tasks = [api_task for _ in range(num_tasks)]

   # Add tasks to the manager
   manager.add_tasks(tasks)
   print(f"Starting execution with {num_keys} API keys for {num_tasks} tasks...")
   start = time.time()
   final_state = manager.execute_all()

   # Print results
   print("Execution completed!")
   print(f"Total time: {time.time() - start:.2f} seconds")
   print(f"Total requests processed: {final_state['request_count']}")

if __name__ == "__main__":
   main()