#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve, Point
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from web3 import Web3
import hashlib
import sys
import os
from typing import List, Optional

# Constants
R_OFFSETS = [-1000, -100, -3, -2, -1, 0, 1, 2, 3, 100, 1000]
CURVE = Curve.get_curve('secp256k1')
CHUNK_SIZE = 1000
OUTPUT_FILE = 'output.txt'

def setup_crypto() -> None:
	"""Initialize cryptographic components."""
	global CURVE
	CURVE = Curve.get_curve('secp256k1')

def sha256_hash(data: bytes) -> str:
	"""Compute SHA256 hash of input bytes and return as hex string."""
	return hashlib.sha256(data).hexdigest()

def generate_ethereum_address(private_key_int: int) -> Optional[str]:
	"""
	Generate Ethereum address from private key integer.
	Returns None if the private key is invalid.
	"""
	try:
		# Validate private key range
		if not (1 <= private_key_int < CURVE.order):
			return None
			
		# Generate public key
		pub_key: Point = private_key_int * CURVE.generator
		
		# Concatenate x and y coordinates (64 bytes)
		concat_xy = pub_key.x.to_bytes(32, byteorder='big') + pub_key.y.to_bytes(32, byteorder='big')
		
		# Compute Keccak-256 hash and take last 40 characters (20 bytes)
		k = keccak.new(digest_bits=256)
		k.update(concat_xy)
		eth_address = '0x' + k.hexdigest()[-40:]
		
		# Return checksum address
		return Web3.to_checksum_address(eth_address)
		
	except (ValueError, ArithmeticError):
		return None

def process_line(line: bytes) -> List[str]:
	"""
	Process a single line from input file and generate key-address pairs.
	Returns list of formatted strings for output.
	"""
	results = []
	line_clean = line.rstrip(b'\n')
	
	if not line_clean:
		return results
		
	base_hash = sha256_hash(line_clean)
	
	for offset in R_OFFSETS:
		try:
			private_key_int = int(base_hash, 16) + offset
			eth_address = generate_ethereum_address(private_key_int)
			
			if eth_address:
				private_key_hex = hex(private_key_int)[2:].zfill(64)
				results.append(f'{private_key_hex} {eth_address}')
				
		except (ValueError, OverflowError):
			continue
			
	return results

def worker_init() -> None:
	"""Initialize worker process for multiprocessing."""
	setup_crypto()

def main() -> None:
	"""Main function to process input file and generate addresses."""
	input_file = 'input.txt'
	
	# Validate input file
	if not os.path.exists(input_file):
		print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
		sys.exit(1)
		
	if os.path.getsize(input_file) == 0:
		print(f"Error: Input file '{input_file}' is empty.", file=sys.stderr)
		sys.exit(1)
	
	# Remove existing output file
	if os.path.exists(OUTPUT_FILE):
		os.remove(OUTPUT_FILE)
	
	# Determine optimal number of processes
	num_processes = min(cpu_count(), 12)  # Cap at 12 to avoid overloading
	
	file_size = os.path.getsize(input_file)
	
	print(f"Processing {file_size:,} bytes with {num_processes} processes...")
	
	with open(input_file, 'rb') as infile, \
		 Pool(processes=num_processes, initializer=worker_init) as pool, \
		 tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing") as pbar:
		
		# Track position for progress updates
		last_position = 0
		
		# Process lines and write results
		with open(OUTPUT_FILE, 'a') as outfile:
			for results in pool.imap_unordered(process_line, infile, chunksize=CHUNK_SIZE):
				# Write results
				if results:
					outfile.write('\n'.join(results) + '\n')
				
				# Update progress
				current_position = infile.tell()
				progress_increment = current_position - last_position
				
				if progress_increment > 0:
					pbar.update(progress_increment)
					last_position = current_position
	
	# Completion signal
	print('\a', end='', file=sys.stderr)
	print(f"\nProcessing complete. Results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
	main()
