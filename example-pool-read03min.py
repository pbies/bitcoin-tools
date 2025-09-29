#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys
import os

def process_line(line_with_pos):
	"""
	Process a single line and return bytes processed.
	
	Args:
		line_with_pos: Tuple of (line_bytes, file_position)
		
	Returns:
		Length of the line in bytes
	"""
	line, position = line_with_pos
	
	try:
		# Process the line
		decoded = line.rstrip(b'\n').decode('utf-8', errors='ignore')
		if decoded.strip():
			# Add your processing logic here
			processed = decoded  # Placeholder
			
			# Write result
			with open('output.txt', 'a', encoding='utf-8') as outfile:
				outfile.write(f"{processed}\n")
				
	except Exception as e:
		# Log error but continue processing
		pass
	
	return len(line)

def line_reader(file_path):
	"""Generator that yields lines with their file positions."""
	with open(file_path, 'rb') as f:
		while True:
			pos = f.tell()
			line = f.readline()
			if not line:
				break
			yield (line, pos)

def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	if not os.path.exists(input_file):
		print(f"Error: {input_file} not found", file=sys.stderr)
		return
	
	total_size = os.path.getsize(input_file)
	print(f"Processing {total_size:,} bytes...", flush=True)
	
	# Initialize output file
	open(output_file, 'w').close()
	
	# Process with accurate progress tracking
	thread_count = min(24, cpu_count() or 4)
	processed_bytes = 0
	update_interval = 10000  # Update progress every ~10KB
	
	with Pool(processes=thread_count) as pool, \
		 tqdm(total=total_size, unit='B', unit_scale=True, desc="Processing") as pbar:
		
		for bytes_processed in pool.imap_unordered(
			process_line, 
			line_reader(input_file),
			chunksize=1000
		):
			processed_bytes += bytes_processed
			pbar.update(bytes_processed)
	
	print(f"\nProcessed {processed_bytes:,} bytes", flush=True)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
