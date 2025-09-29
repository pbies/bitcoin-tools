#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from multiprocessing import Pool
from tqdm import tqdm
from typing import Optional
from web3 import Web3
import hashlib
import os
import sys

# Configuration
INPUT_FILE = 'input.txt'
OUTPUT_FILE = 'output.txt'
CHUNK_SIZE = 1000
PROCESSES = 24
UPDATE_INTERVAL = 10000
CURVE_NAME = 'secp256k1'

class EthereumAddressGenerator:
	def __init__(self):
		self.cv = Curve.get_curve(CURVE_NAME)
		self.curve_order = self.cv.order
	
	def process_line(self, line: bytes) -> Optional[str]:
		"""Process a single line and return formatted result or None on failure"""
		line = line.rstrip(b'\n')
		if not line:
			return None
		
		try:
			# Generate private key from SHA256 hash
			x = hashlib.sha256(line).hexdigest()
			private_key = int(x, 16) % self.curve_order
			
			# Generate public key
			pu_key = private_key * self.cv.generator
			
			# Convert to Ethereum address
			concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
			
			k = keccak.new(digest_bits=256)
			k.update(concat_x_y)
			eth_addr = '0x' + k.hexdigest()[-40:]
			
			# Add checksum
			cksum = Web3.to_checksum_address(eth_addr)
			
			return f'{cksum} {x} {line.decode("utf-8", errors="ignore")}'
			
		except Exception as e:
			# Log error but don't crash the process
			print(f"Error processing line: {e}", file=sys.stderr)
			return None

def init_worker():
	"""Initialize worker process"""
	global generator
	generator = EthereumAddressGenerator()

def process_line_wrapper(line: bytes) -> Optional[str]:
	"""Wrapper function for multiprocessing"""
	return generator.process_line(line)

def main():
	# Check if input file exists
	if not os.path.exists(INPUT_FILE):
		print(f"Error: Input file '{INPUT_FILE}' not found", file=sys.stderr)
		sys.exit(1)
	
	# Get file size for progress bar
	try:
		file_size = os.path.getsize(INPUT_FILE)
	except OSError as e:
		print(f"Error accessing file: {e}", file=sys.stderr)
		sys.exit(1)
	
	# Clear output file at start
	open(OUTPUT_FILE, 'w').close()
	
	generator = EthereumAddressGenerator()
	processed_count = 0
	
	print(f"Processing {INPUT_FILE} ({file_size} bytes) with {PROCESSES} processes...")
	
	try:
		with open(INPUT_FILE, 'rb') as infile, \
			 Pool(processes=PROCESSES, initializer=init_worker) as pool, \
			 tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
			
			# Process lines in parallel
			for result in pool.imap_unordered(process_line_wrapper, infile, chunksize=CHUNK_SIZE):
				if result:
					# Write valid results to output file
					with open(OUTPUT_FILE, 'a') as outfile:
						outfile.write(result + '\n')
				
				# Update progress based on file position
				current_pos = infile.tell()
				progress = current_pos - pbar.n
				if progress > 0:
					pbar.update(progress)
				
				processed_count += 1
				
	except KeyboardInterrupt:
		print("\nProcessing interrupted by user", file=sys.stderr)
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error: {e}", file=sys.stderr)
		sys.exit(1)
	
	# Completion signal
	print('\a', end='', file=sys.stderr)
	print(f"\nProcessing complete! Processed {processed_count} lines.")
	print(f"Results saved to {OUTPUT_FILE}")

if __name__ == '__main__':
	main()
