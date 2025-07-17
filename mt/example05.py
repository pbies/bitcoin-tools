#!/usr/bin/env python3

import concurrent.futures
import time
import math

def cpu_bound_task(x):
	"""A CPU-bound task that performs heavy computation"""
	return math.sqrt(x ** 3 + x ** 2 + x)

def io_bound_task(x):
	"""An I/O-bound task that simulates waiting (like network/database calls)"""
	time.sleep(0.1)  # Simulate I/O wait
	return x * x

def run_sequential(func, data):
	start = time.perf_counter()
	results = [func(x) for x in data]
	duration = time.perf_counter() - start
	print(f"Sequential execution completed in {duration:.4f} seconds")
	return results

def run_threaded(func, data, max_workers=5):
	start = time.perf_counter()
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		results = list(executor.map(func, data))
	duration = time.perf_counter() - start
	print(f"Threaded execution ({max_workers} workers) completed in {duration:.4f} seconds")
	return results

def run_multiprocessed(func, data, max_workers=5):
	start = time.perf_counter()
	with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
		results = list(executor.map(func, data))
	duration = time.perf_counter() - start
	print(f"Multiprocess execution ({max_workers} workers) completed in {duration:.4f} seconds")
	return results

if __name__ == "__main__":
	# Test data
	test_data = list(range(1, 20))
	
	print("Testing I/O-bound task (threading is most effective here):")
	run_sequential(io_bound_task, test_data)
	run_threaded(io_bound_task, test_data, max_workers=5)
	run_threaded(io_bound_task, test_data, max_workers=10)
	
	print("\nTesting CPU-bound task (threading won't help much due to GIL):")
	run_sequential(cpu_bound_task, test_data)
	run_threaded(cpu_bound_task, test_data, max_workers=5)

	print("\nTesting I/O-bound task - multiprocessed:")
	run_multiprocessed(io_bound_task, test_data, max_workers=5)

	print("\nTesting CPU-bound task - multiprocessed:")
	run_multiprocessed(cpu_bound_task, test_data, max_workers=5)
