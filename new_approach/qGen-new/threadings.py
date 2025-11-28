import threading
import queue
import time
import random


# 1. setting up the data. 
X = [f"item_{i}" for i in range(20) ]
api_keys = [f"key_{i}" for i in range(7) ]

# creation of shared work queue

work_queue = queue.Queue()

for item in X: 
    work_queue.put(item)

# 3. Defining the worker function
work_report = {}
def worker_action(thread_id, api_key):
    while True:
        try:
            # trying to get a item indefinitely without blocking indefinitely
            item = work_queue.get(block = False)
            
        except queue.Empty:
            print("no item left in the queue")
            break
        print(f"Thread {thread_id} processing {item}")

        if item in work_report:
            raise ValueError(f"Item {item} already processed by thread {work_report[item][0]} and api_key {work_report[item][1]}")
        work_report[item] = [thread_id, api_key]
        
        i = 0
        start = time.time()
        random_wait = random.randint(2, 5)
        time.sleep(random_wait)
        end_time = time.time()
        if (end_time - start) <  random_wait:
            raise ValueError("Thread is not working sequentially inside the queue")

        work_queue.task_done()

# 4. Creating the threads:
threads = []
for i, key in enumerate(api_keys):
    t = threading.Thread(target = worker_action, args = (i, key))
    t.start()
    threads.append(t)

# wait for completion
for t in threads:
    t.join()

print("All tasks are executed\nWORK REPORT\n")
for item_name, (thread_id, api_key) in work_report.items():
    print(f"{item_name} : {thread_id} ; {api_key}")