#!/usr/bin/env python3

# this script does not work

from tqdm.contrib.concurrent import process_map
import os
import sys
from pathlib import Path
from typing import Iterator
import fcntl  # For file locking on Unix systems


def setup_output_file(output_file: str) -> None:
	"""Initialize output file and ensure directory exists."""
	output_path = Path(output_file)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.touch()  # Create empty file


def process_line(line: str) -> str:
	"""
	Process a single line and return the result.
	Replace this with your actual processing logic.
	"""
	line = line.strip()
	if not line:
		return None
	
	# Add your actual processing logic here
	# Example: base58 encoding, hashing, regex, etc.
	# processed = base58.b58encode(line.encode()).decode()
	# hashed = hashlib.sha256(line.encode()).hexdigest()
	
	# For now, just return the line in uppercase as example
	return line.upper()


def write_result(result: str, output_file: str) -> None:
	"""Safely write a single result to the output file with locking."""
	if not result:
		return
	
	try:
		# Use file locking to prevent interleaved writes
		with open(output_file, 'a', encoding='utf-8') as outfile:
			# Try to acquire lock (Unix systems)
			try:
				fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
			except (AttributeError, ImportError):
				# Locking not available on this system, proceed without
				pass
			
			outfile.write(result + '\n')
			outfile.flush()  # Ensure immediate write
			
	except IOError as e:
		print(f"Error writing to output file: {e}", file=sys.stderr)
		raise


def process_and_write_chunk(lines_chunk: list, output_file: str) -> None:
	"""Process a chunk of lines and write results."""
	for line in lines_chunk:
		result = process_line(line)
		if result:
			write_result(result, output_file)


def read_lines_in_chunks(file_path: str, chunk_size: int = 1000) -> Iterator[list]:
	"""Read file in chunks to manage memory usage."""
	with open(file_path, 'r', encoding='utf-8') as infile:
		chunk = []
		for line in infile:
			chunk.append(line)
			if len(chunk) >= chunk_size:
				yield chunk
				chunk = []
		if chunk:  # Don't forget the last chunk
			yield chunk


def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	# Validate input file
	if not os.path.exists(input_file):
		print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
		sys.exit(1)
	
	# Get file size for progress estimation
	file_size = os.path.getsize(input_file)
	print(f"Input file size: {file_size:,} bytes", flush=True)
	
	# Count lines for progress bar
	print("Counting lines...", flush=True)
	with open(input_file, 'r', encoding='utf-8') as f:
		line_count = sum(1 for _ in f)
	print(f"Processing {line_count:,} lines...", flush=True)
	
	if line_count == 0:
		print("Input file is empty.", file=sys.stderr)
		sys.exit(1)
	
	# Setup output file
	setup_output_file(output_file)
	
	# Process in chunks to manage memory
	try:
		chunks = list(read_lines_in_chunks(input_file, chunk_size=1000))
		
		# Process chunks in parallel
		process_map(
			lambda chunk: process_and_write_chunk(chunk, output_file),
			chunks,
			max_workers=min(24, os.cpu_count() or 1),
			chunksize=1,  # Each chunk is already a batch of lines
			desc="Processing lines"
		)
		
	except Exception as e:
		print(f"Error during processing: {e}", file=sys.stderr)
		sys.exit(1)
	
	# Verify output
	output_lines = 0
	if os.path.exists(output_file):
		with open(output_file, 'r', encoding='utf-8') as f:
			output_lines = sum(1 for _ in f)
	
	print(f"\nProcessing complete! Input: {line_count:,} lines, Output: {output_lines:,} lines", flush=True)
	print('\a', end='', file=sys.stderr)  # Terminal bell


if __name__ == '__main__':
	main()
