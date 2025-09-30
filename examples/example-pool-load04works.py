#!/usr/bin/env python3

# this script is the fastest

from ecdsa import SigningKey, SECP256k1
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import List, Optional
import logging
import os
import signal
import sys
import base58
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

order = SECP256k1.order
hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def init_worker():
	"""Initialize worker process to ignore interrupt signals."""
	signal.signal(signal.SIGINT, signal.SIG_IGN)


def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()


def process_item(line: str) -> Optional[str]:
	try:
		line = line.strip()
		if not line:
			return None
		
		p=entropy_to_pvk(line)
		if p==None:
			return
		try:
			w=pvk_to_wif2(p)
			hdwallet.from_private_key(p)
		except:
			return
		r=f'{w}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		
		return r
		
	except Exception as e:
		logger.error(f"Error processing line '{line[:50]}...': {e}")
		return None


def validate_files(input_file: str, output_file: str) -> bool:
	"""Validate that input file exists and output directory is writable."""
	input_path = Path(input_file)
	output_path = Path(output_file)
	
	if not input_path.exists():
		logger.error(f"Input file '{input_file}' not found")
		return False
	
	if input_path.stat().st_size == 0:
		logger.error("Input file is empty")
		return False
	
	# Check if output directory is writable
	output_dir = output_path.parent
	if not output_dir.exists():
		output_dir.mkdir(parents=True, exist_ok=True)
	
	if not os.access(output_dir, os.W_OK):
		logger.error(f"Output directory '{output_dir}' is not writable")
		return False
	
	return True


def read_lines_chunked(file_obj, chunk_size: int = 10000) -> List[str]:
	"""
	Read lines from file object in chunks to manage memory usage.
	
	Args:
		file_obj: Open file object
		chunk_size: Number of lines to read at once
		
	Returns:
		List of lines
	"""
	lines = []
	for i in range(chunk_size):
		line = file_obj.readline()
		if not line:  # End of file
			break
		lines.append(line)
	return lines


def write_results(results: List[str], output_file: str) -> None:
	"""Write processed results to output file."""
	if not results:
		return
	
	try:
		with open(output_file, 'a', encoding='utf-8') as f:
			for result in results:
				if result is not None:
					f.write(result)
	except IOError as e:
		logger.error(f"Error writing to output file: {e}")
		raise


def main():
	input_file = 'input.txt'
	output_file = 'output.txt'
	
	# Validate files
	if not validate_files(input_file, output_file):
		sys.exit(1)
	
	# Get optimal worker count
	available_cpus = cpu_count()
	worker_count = min(24, available_cpus) if available_cpus else 4
	logger.info(f"Using {worker_count} processes (available CPUs: {available_cpus})")
	
	# Initialize output file (truncate if exists)
	try:
		with open(output_file, 'w') as f:
			pass  # Just create/truncate the file
		logger.info("Output file initialized (cleared if existed)")
	except IOError as e:
		logger.error(f"Failed to initialize output file: {e}")
		sys.exit(1)
	
	# Process file in chunks to manage memory
	total_processed = 0
	chunk_size = 10000
	chunk_number = 0
	
	try:
		with Pool(processes=worker_count, initializer=init_worker) as pool:
			# Open the input file once and keep it open
			with open(input_file, 'r', encoding='utf-8') as input_f:
				while True:
					# Read chunk of lines from current position
					chunk_number += 1
					logger.info(f"Reading chunk {chunk_number} of up to {chunk_size} lines...")
					lines_chunk = read_lines_chunked(input_f, chunk_size)
					
					if not lines_chunk:
						break  # End of file
					
					# Process chunk
					logger.info(f"Processing {len(lines_chunk)} lines (chunk {chunk_number})...")
					with tqdm(total=len(lines_chunk), desc=f"Chunk {chunk_number}") as pbar:
						results = []
						for result in pool.imap_unordered(process_item, lines_chunk, chunksize=100):
							if result is not None:
								results.append(result)
							pbar.update(1)
					
					# Write results
					if results:
						write_results(results, output_file)
						logger.info(f"Written {len(results)} results to output")
					
					total_processed += len(lines_chunk)
					logger.info(f"Total processed: {total_processed} lines")
					
					# If we read less than chunk_size, we've reached end of file
					if len(lines_chunk) < chunk_size:
						break
					
	except KeyboardInterrupt:
		logger.info("Processing interrupted by user")
	except Exception as e:
		logger.error(f"Unexpected error during processing: {e}")
		import traceback
		traceback.print_exc()
		sys.exit(1)
	
	# Final statistics
	if Path(output_file).exists():
		output_size = Path(output_file).stat().st_size
		try:
			with open(output_file, 'r', encoding='utf-8') as f:
				output_lines = sum(1 for _ in f)
			logger.info(f"Processing complete! Output file: {output_lines} lines, {output_size:,} bytes")
		except:
			logger.info(f"Processing complete! Output file size: {output_size:,} bytes")
	
	print('\a', end='', file=sys.stderr)  # Terminal bell
	logger.info("Processing finished")


if __name__ == '__main__':
	main()
