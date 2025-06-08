#!/usr/bin/env python3

import concurrent.futures
import time

def task(n):
	print(f"Task {n} started")
	time.sleep(2)
	result = n * n
	print(f"Task {n} finished. Result: {result}")
	return result

# Using ThreadPoolExecutor (threads)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
	results = list(executor.map(task, range(10)))
	print(results)

# Using ProcessPoolExecutor (processes)
with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
	results = list(executor.map(task, range(10)))
	print(results)

# Using ThreadPoolExecutor with imap (lazy evaluation)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
	future_to_task = {}
	for i in range(10):
		future = executor.submit(task, i)
		future_to_task[future] = i
	results = []
	for future in concurrent.futures.as_completed(future_to_task):
		task_num = future_to_task[future]
		try:
			result = future.result()
			print(f"Task {task_num} finished. Result: {result}")
			results.append(result)
		except Exception as e:
			print(f"Task {task_num} raised an exception: {e}")
	print(results)
