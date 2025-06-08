#!/usr/bin/env python3

import multiprocessing

def process_data(data):
	"""Your data processing function that takes (index, value) and returns (index, processed_value)"""
	idx, value = data  # Unpack the input tuple
	# Example processing - replace with your actual processing logic
	result = value * 2  # Just an example transformation
	return (idx, result)  # Return index with result

def main():
	# Example input data
	input_data = [5, 2, 8, 1, 9, 3]
	
	# Create a pool of workers
	with multiprocessing.Pool() as pool:
		# Use imap_unordered with enumerated data
		# Each item is a tuple (index, value)
		results = pool.imap_unordered(process_data, enumerate(input_data))
		
		# Create a list to store results (unordered at first)
		unordered_results = list(results)
		
		# Sort the results based on the original index (first element of each tuple)
		sorted_results = [result for idx, result in sorted(unordered_results)]
		
		print("Original input data:", input_data)
		print("Processed results (unordered):", unordered_results)
		print("Processed results (sorted):", sorted_results)

if __name__ == '__main__':
	main()
