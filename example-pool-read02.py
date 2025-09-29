#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys
import os
from pathlib import Path
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s',
	datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class FileProcessor:
	"""Handles file processing with progress tracking and error handling."""
	
	def __init__(self, input_file: str, output_file: str):
		self.input_file = input_file
		self.output_file = output_file
		self.processed_bytes = 0
		self.last_position = 0
		
	def validate_files(self) -> bool:
		"""Validate that input file exists and output can be written."""
		if not os.path.exists(self.input_file):
			logger.error(f"Input file '{self.input_file}' not found")
			return False
		
		if os.path.getsize(self.input_file) == 0:
			logger.error("Input file is empty")
			return False
		
		# Ensure output directory exists and is writable
		output_path = Path(self.output_file)
		output_path.parent.mkdir(parents=True, exist_ok=True)
		
		try:
			# Test write access
			with open(self.output_file, 'w') as f:
				pass
			return True
		except IOError as e:
			logger.error(f"Cannot write to output file: {e}")
			return False
	
	def process_line(self, line: bytes) -> Optional[str]:
		"""
		Process a single line from the input file.
		Replace this with your actual processing logic.
		
		Args:
			line: Raw bytes from input file
			
		Returns:
			Processed string to write, or None to skip
		"""
		try:
			# Remove trailing newline and decode
			decoded_line = line.rstrip(b'\n').decode('utf-8')
			
			if not decoded_line.strip():
				return None
			
			# Add your actual processing logic here
			# Example: base58 encoding, hashing, etc.
			# processed = base58.b58encode(decoded_line.encode()).decode()
			# processed = some_other_processing(decoded_line)
			
			# Placeholder - return the line as-is
			processed = decoded_line
			
			return f"{processed}\n"
			
		except UnicodeDecodeError:
			logger.warning(f"Skipping line due to encoding issue: {line[:50]}...")
			return None
		except Exception as e:
			logger.error(f"Error processing line: {e}")
			return None
	
	def write_result(self, result: str) -> None:
		"""Safely write a result to the output file."""
		if not result:
			return
		
		try:
			with open(self.output_file, 'a', encoding='utf-8') as outfile:
				outfile.write(result)
		except IOError as e:
			logger.error(f"Failed to write to output file: {e}")
			raise
	
	def process_chunk(self, args) -> int:
		"""
		Process a chunk of lines and return bytes processed.
		
		Args:
			args: Tuple of (line, current_file_position)
			
		Returns:
			Number of bytes processed in this chunk
		"""
		line, position = args
		result = self.process_line(line)
		if result:
			self.write_result(result)
		return len(line)
	
	def line_generator(self):
		"""
		Generator that yields lines with their file positions.
		This allows accurate progress tracking.
		"""
		try:
			with open(self.input_file, 'rb') as f:
				while True:
					pos = f.tell()
					line = f.readline()
					if not line:
						break
					yield (line, pos)
		except IOError as e:
			logger.error(f"Error reading input file: {e}")
			raise


def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	# Initialize processor
	processor = FileProcessor(input_file, output_file)
	
	# Validate files
	if not processor.validate_files():
		sys.exit(1)
	
	# Get file size for progress tracking
	total_size = os.path.getsize(input_file)
	logger.info(f"Input file size: {total_size:,} bytes")
	
	# Determine optimal thread count
	available_cpus = cpu_count()
	thread_count = min(24, available_cpus) if available_cpus else 4
	logger.info(f"Using {thread_count} processes")
	
	# Clear output file
	try:
		open(output_file, 'w').close()
		logger.info("Output file initialized")
	except IOError as e:
		logger.error(f"Failed to initialize output file: {e}")
		sys.exit(1)
	
	# Process file with progress tracking
	try:
		with Pool(processes=thread_count) as pool, \
			 tqdm(total=total_size, unit='B', unit_scale=True, 
				  unit_divisor=1024, desc="Processing") as pbar:
			
			# Process lines with progress updates
			processed_bytes = 0
			update_threshold = min(1024 * 1024, total_size // 100)  # 1MB or 1% of file
			
			for bytes_processed in pool.imap_unordered(
				processor.process_chunk, 
				processor.line_generator(),
				chunksize=1000
			):
				processed_bytes += bytes_processed
				
				# Update progress bar in chunks to reduce overhead
				if processed_bytes - processor.last_position >= update_threshold:
					pbar.update(processed_bytes - processor.last_position)
					processor.last_position = processed_bytes
					pbar.refresh()
			
			# Update progress bar with any remaining bytes
			if processed_bytes > processor.last_position:
				pbar.update(processed_bytes - processor.last_position)
			
			logger.info(f"Processing complete: {processed_bytes:,} bytes processed")
			
	except KeyboardInterrupt:
		logger.info("Processing interrupted by user")
	except Exception as e:
		logger.error(f"Unexpected error during processing: {e}")
		sys.exit(1)
	
	# Verify output
	if os.path.exists(output_file):
		output_size = os.path.getsize(output_file)
		logger.info(f"Output file size: {output_size:,} bytes")
	
	print('\a', end='', file=sys.stderr)  # Terminal bell
	logger.info("Script execution finished")


if __name__ == '__main__':
	main()
