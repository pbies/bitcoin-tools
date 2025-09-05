#!/usr/bin/env python3

import time

def time_call(func, *args, **kwargs):
	start = time.perf_counter()
	result = func(*args, **kwargs)
	end = time.perf_counter()
	print(f"{func.__name__} took {end - start:.3f} seconds")
	return result

# Example usage:
def my_function(n):
	return sum(range(n))

# Time one call
time_call(my_function, 1_000_000_00)
