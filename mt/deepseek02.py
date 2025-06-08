#!/usr/bin/env python3

import time
import threading
import concurrent.futures
import multiprocessing
from queue import Queue
from multiprocessing import Pool

# Benchmark tasks
def cpu_bound_task(n):
	"""Calculate nth Fibonacci number (CPU-bound task)"""
	if n <= 1:
		return n
	else:
		return cpu_bound_task(n-1) + cpu_bound_task(n-2)

def io_bound_task(duration):
	"""Simulate I/O-bound task with sleep"""
	time.sleep(duration)

# Test functions for different approaches
def sequential_approach(tasks, task_func, *args):
	start_time = time.time()
	for task in tasks:
		task_func(task, *args)
	return time.time() - start_time

def threading_approach(tasks, task_func, *args):
	start_time = time.time()
	threads = []
	for task in tasks:
		thread = threading.Thread(target=task_func, args=(task, *args))
		thread.start()
		threads.append(thread)
	
	for thread in threads:
		thread.join()
	return time.time() - start_time

def thread_pool_executor_approach(tasks, task_func, *args):
	start_time = time.time()
	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(task_func, task, *args) for task in tasks]
		for future in concurrent.futures.as_completed(futures):
			future.result()
	return time.time() - start_time

def process_pool_executor_approach(tasks, task_func, *args):
	start_time = time.time()
	with concurrent.futures.ProcessPoolExecutor() as executor:
		futures = [executor.submit(task_func, task, *args) for task in tasks]
		for future in concurrent.futures.as_completed(futures):
			future.result()
	return time.time() - start_time

def multiprocessing_pool_approach(tasks, task_func, *args):
	start_time = time.time()
	with Pool() as pool:
		pool.starmap(task_func, [(task, *args) for task in tasks])
	return time.time() - start_time

def queue_based_approach(tasks, task_func, *args):
	start_time = time.time()
	q = Queue()
	
	def worker():
		while True:
			task = q.get()
			if task is None:
				break
			task_func(task, *args)
			q.task_done()
	
	# Start worker threads
	num_workers = multiprocessing.cpu_count()
	threads = []
	for _ in range(num_workers):
		t = threading.Thread(target=worker)
		t.start()
		threads.append(t)
	
	# Add tasks to queue
	for task in tasks:
		q.put(task)
	
	# Block until all tasks are done
	q.join()
	
	# Stop workers
	for _ in range(num_workers):
		q.put(None)
	for t in threads:
		t.join()
	
	return time.time() - start_time

def run_benchmark(task_type, task_size, approaches):
	"""Run benchmark for given task type and approaches"""
	print(f"\n=== Benchmarking {task_type} tasks ({task_size} tasks) ===")
	
	if task_type == "CPU-bound":
		tasks = [35] * task_size  # Calculating 35th Fibonacci number
		task_func = cpu_bound_task
	else:  # I/O-bound
		tasks = [0.1] * task_size  # 0.1 second sleep
		task_func = io_bound_task
	
	results = {}
	for approach_name, approach_func in approaches.items():
		print(f"Running {approach_name}...", end=' ', flush=True)
		try:
			duration = approach_func(tasks, task_func)
			results[approach_name] = duration
			print(f"{duration:.2f} seconds")
		except Exception as e:
			results[approach_name] = str(e)
			print(f"Error: {e}")
	
	return results

def print_results(results):
	"""Print benchmark results in a table"""
	print("\nBenchmark Results:")
	print("{:<25} {:<15}".format('Approach', 'Time (seconds)'))
	print("-" * 40)
	for approach, time_taken in results.items():
		if isinstance(time_taken, str):
			print("{:<25} {:<15}".format(approach, time_taken))
		else:
			print("{:<25} {:<15.2f}".format(approach, time_taken))

if __name__ == "__main__":
	# Define approaches to test
	approaches = {
		"Sequential": sequential_approach,
		"Threading": threading_approach,
		"ThreadPoolExecutor": thread_pool_executor_approach,
		"ProcessPoolExecutor": process_pool_executor_approach,
		"Multiprocessing.Pool": multiprocessing_pool_approach,
		"Queue-based": queue_based_approach
	}
	
	# Number of tasks to benchmark with
	cpu_task_size = 10
	io_task_size = 20
	
	# Run benchmarks
	print(f"\nSystem has {multiprocessing.cpu_count()} CPU cores")
	
	cpu_results = run_benchmark("CPU-bound", cpu_task_size, approaches)
	io_results = run_benchmark("I/O-bound", io_task_size, approaches)
	
	# Print results
	print("\n=== CPU-bound Task Results ===")
	print(f"(Calculating Fibonacci(35) {cpu_task_size} times)")
	print_results(cpu_results)
	
	print("\n=== I/O-bound Task Results ===")
	print(f"(Sleeping for 0.1s {io_task_size} times)")
	print_results(io_results)
