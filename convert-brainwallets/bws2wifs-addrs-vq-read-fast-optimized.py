#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os, hashlib, base58, sys
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

# Increase chunk size significantly for better multiprocessing efficiency
CHUNK_LINES = 1000

# Initialize HDWallet once per process (in the worker)
_process_hdwallet = None

def init_worker():
	"""Initialize HDWallet once per worker process"""
	global _process_hdwallet
	_process_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_block(lines):
	"""Process a block of lines using pre-initialized HDWallet"""
	hdwallet = _process_hdwallet
	results = []
	
	for line in lines:
		line = line.rstrip(b'\n')
		sha = hashlib.sha256(line).digest()
		h = sha.hex()
		
		hdwallet.from_private_key(private_key=h)
		wif = pvk_to_wif2(h)
		
		# Use list for efficient string building
		results.extend([
			line.decode('utf-8', errors='ignore'),
			'\n',
			wif,
			'\n',
			hdwallet.wif(),
			'\n',
			hdwallet.address('P2PKH'),
			'\n',
			hdwallet.address('P2SH'),
			'\n',
			hdwallet.address('P2TR'),
			'\n',
			hdwallet.address('P2WPKH'),
			'\n',
			hdwallet.address('P2WPKH-In-P2SH'),
			'\n',
			hdwallet.address('P2WSH'),
			'\n',
			hdwallet.address('P2WSH-In-P2SH'),
			'\n\n'
		])
	
	return ''.join(results)

def read_blocks(path, chunk_size=CHUNK_LINES):
	"""Read file in chunks efficiently"""
	with open(path, 'rb', buffering=4*1024*1024) as f:  # Larger buffer
		block = []
		for line in f:
			block.append(line)
			if len(block) >= chunk_size:
				yield block
				block = []
		if block:
			yield block

def main():
	inp = 'input.txt'
	out = 'output.txt'

	total_bytes = os.path.getsize(inp)

	# Clear output file
	with open(out, 'w'):
		pass

	workers = cpu_count()

	# FIX: Don't read the file twice! Store blocks in a list
	with Pool(workers, initializer=init_worker) as p, \
		 open(out, 'a', buffering=4*1024*1024) as fo, \
		 tqdm(total=total_bytes, unit='B', unit_scale=True) as bar:

		blocks = list(read_blocks(inp))
		
		for block, result in zip(blocks, p.imap_unordered(process_block, blocks, chunksize=1)):
			fo.write(result)
			bar.update(sum(len(line) for line in block))

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
