#!/usr/bin/env python3

import concurrent.futures as cf
import time

def sleep_and_print(num):
	print(f"Task {num} started")
	time.sleep(1)
	print(f"Task {num} finished")

# Using ThreadPoolExecutor (threads)
with cf.ThreadPoolExecutor(max_workers=3) as executor:
	futures = [executor.submit(sleep_and_print, i) for i in range(10)]
	for future in cf.as_completed(futures):
		future.result()

# Using ProcessPoolExecutor (processes)
with cf.ProcessPoolExecutor(max_workers=3) as executor:
	futures = [executor.submit(sleep_and_print, i) for i in range(10)]
	for future in cf.as_completed(futures):
		future.result()
