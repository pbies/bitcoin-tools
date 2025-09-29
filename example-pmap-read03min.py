#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
import os
import sys
from contextlib import contextmanager

@contextmanager
def synchronized_writer(output_file):
	"""Thread-safe file writer."""
	with open(output_file, 'a', encoding='utf-8') as f:
		# Simple synchronization for writing
		yield f

def process_line(line):
	"""Process a single line."""
	line = line.strip()
	if not line:
		return None
	
	# Add your processing logic here
	return line.upper()  # Example

def process_and_write(args):
	"""Process line and write result."""
	line, output_file = args
	result = process_line(line)
	if result:
		with synchronized_writer(output_file) as outfile:
			outfile.write(result + '\n')

def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	if not os.path.exists(input_file):
		print(f"Error: Input file not found", file=sys.stderr)
		return
	
	# Create empty output file
	open(output_file, 'w').close()
	
	# Read all lines
	with open(input_file, 'r') as f:
		lines = [line for line in f if line.strip()]
	
	# Create arguments for workers
	tasks = [(line, output_file) for line in lines]
	
	# Process in parallel
	process_map(
		process_and_write,
		tasks,
		max_workers=min(12, os.cpu_count() or 1),  # Reduced workers for file I/O
		chunksize=100
	)
	
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
