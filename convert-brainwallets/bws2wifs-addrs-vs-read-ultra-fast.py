#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os, base58, sys
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

# Larger chunks = better multiprocessing efficiency
CHUNK_LINES = 2000

# Process-local HDWallet instance
_process_hdwallet = None

def init_worker():
	"""Initialize HDWallet once per worker process"""
	global _process_hdwallet
	_process_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	"""Fast WIF conversion"""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_block(lines):
	"""Process a block of lines with optimized string building.
	Returns (result_str, byte_count) so the caller can update the progress bar
	without needing to keep a reference to the original block."""
	hdwallet = _process_hdwallet
	output_parts = []
	byte_count = 0

	for line in lines:
		byte_count += len(line)
		line = line.rstrip(b'\n')
		h = line.hex()
		if len(h) > 64:
			h = h[0:64]
		h = h.zfill(64)

		try:
			hdwallet.from_private_key(private_key=h)
		except:
			continue

		wif_manual    = pvk_to_wif2(h)
		wif_hdwallet  = hdwallet.wif()
		p2pkh         = hdwallet.address('P2PKH')
		p2sh          = hdwallet.address('P2SH')
		p2tr          = hdwallet.address('P2TR')
		p2wpkh        = hdwallet.address('P2WPKH')
		p2wpkh_p2sh   = hdwallet.address('P2WPKH-In-P2SH')
		p2wsh         = hdwallet.address('P2WSH')
		p2wsh_p2sh    = hdwallet.address('P2WSH-In-P2SH')

		output_parts.append(
			f"{line.decode('utf-8', errors='ignore')}\n"
			f"{wif_manual}\n"
			f"{wif_hdwallet}\n"
			f"{p2pkh}\n"
			f"{p2sh}\n"
			f"{p2tr}\n"
			f"{p2wpkh}\n"
			f"{p2wpkh_p2sh}\n"
			f"{p2wsh}\n"
			f"{p2wsh_p2sh}\n\n"
		)

	return ''.join(output_parts), byte_count

def read_blocks(path, chunk_size=CHUNK_LINES):
	"""Lazily yield blocks of lines from the file — never loads the whole file."""
	with open(path, 'rb', buffering=8*1024*1024) as f:
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

	if not os.path.exists(inp):
		print(f"Error: {inp} not found!", file=sys.stderr)
		return

	total_bytes = os.path.getsize(inp)

	# Clear output file
	open(out, 'w').close()

	workers = max(1, cpu_count() - 2)
	print(f"Using {workers} worker processes", file=sys.stderr)

	with Pool(workers, initializer=init_worker) as p, \
		 open(out, 'a', buffering=8*1024*1024) as fo, \
		 tqdm(total=total_bytes, unit='B', unit_scale=True, desc="Processing") as bar:

		# imap_unordered consumes the generator lazily: each block is read
		# from disk only as a worker becomes free, so memory stays bounded.
		for result_str, byte_count in p.imap_unordered(
			process_block,
			read_blocks(inp),
			chunksize=1,
		):
			fo.write(result_str)
			bar.update(byte_count)

	print('\nDone!', file=sys.stderr)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
