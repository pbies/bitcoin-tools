#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os, base58, sys, hashlib
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_LINES = 2000
ADDR_TYPES = ('P2PKH', 'P2SH', 'P2TR', 'P2WPKH', 'P2WPKH-In-P2SH', 'P2WSH', 'P2WSH-In-P2SH')

_wallets = None

def init_worker():
	global _wallets
	_wallets = [HDWallet(cryptocurrency=BTC, hd=BIP32HD) for _ in range(9)]

def pvk_to_wif(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_block(lines):
	output_parts = []
	byte_count = 0

	for line in lines:
		byte_count += len(line)
		raw = line.rstrip(b'\n')
		s = raw.decode()
		b = bytes.fromhex(s)
		tmp1 = b[0::2]
		tmp2 = b[1::2]
		h3 = tmp1 + tmp2
		h4 = tmp2 + tmp1
		keys = [s, b[::-1].hex(), s[::-1], h3.hex(), h4.hex(), h3.hex()[::-1], h4.hex()[::-1], h3[::-1].hex(), h4[::-1].hex() ]
		label = raw.decode('utf-8', errors='ignore')

		for hw, key in zip(_wallets, keys):
			#try:
			#print(key)
			hw.from_private_key(private_key=key)
			#except Exception:
			#	continue
			addrs = '\n'.join(hw.address(a) for a in ADDR_TYPES)
			output_parts.append(
				f"{label}\n{pvk_to_wif(key)}\n{hw.wif()}\n{addrs}\n\n"
			)

	return ''.join(output_parts), byte_count

def read_blocks(path, chunk_size=CHUNK_LINES):
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

	open(out, 'w').close()
	workers = max(1, cpu_count() - 2)
	print(f"Using {workers} worker processes", file=sys.stderr)

	with Pool(workers, initializer=init_worker) as p, \
		 open(out, 'a', buffering=8*1024*1024) as fo, \
		 tqdm(total=os.path.getsize(inp), unit='B', unit_scale=True, desc="Processing") as bar:

		for result_str, byte_count in p.imap_unordered(process_block, read_blocks(inp), chunksize=1):
			fo.write(result_str)
			bar.update(byte_count)

	print('\nDone!', file=sys.stderr)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
