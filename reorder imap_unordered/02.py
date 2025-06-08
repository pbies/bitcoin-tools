#!/usr/bin/env python3

import multiprocessing
import heapq

def process_data(data):
	"""Your data processing function"""
	idx, value = data  # Unpack the input tuple
	# Example processing - replace with your actual processing logic
	result = value * 2  # Just an example transformation
	return (idx, result)  # Return index with result

def main():
	# Example input data
	input_data = [5, 2, 8, 1, 9, 3]
	
	# Create a pool of workers
	with multiprocessing.Pool() as pool:
		# Process data with indices
		results = pool.imap_unordered(process_data, enumerate(input_data))
		
		# Use a heap to sort results as they come in
		heap = []
		for result in results:
			heapq.heappush(heap, result)
		
		# Extract results in order
		sorted_results = [heapq.heappop(heap)[1] for _ in range(len(heap))]
		
		print("Original input data:", input_data)
		print("Processed results (sorted):", sorted_results)

if __name__ == '__main__':
	main()
