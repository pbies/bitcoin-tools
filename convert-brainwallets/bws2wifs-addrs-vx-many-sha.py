#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os, base58, sys, hashlib
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_LINES = 10
ADDR_TYPES = ('P2PKH', 'P2SH', 'P2TR', 'P2WPKH', 'P2WPKH-In-P2SH', 'P2WSH', 'P2WSH-In-P2SH')

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

_wallets = None

def init_worker():
	global _wallets
	_wallets = [HDWallet(cryptocurrency=BTC, hd=BIP32HD) for _ in range(3)]

def pvk_to_wif(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def key_valid(key_hex):
	try:
		n = int(key_hex, 16)
	except ValueError:
		return False
	return 0 < n < SECP256K1_ORDER

def process_block(lines):
	output_parts = []
	byte_count = 0

	for line in lines:
		byte_count += len(line)
		raw = line.rstrip(b'\n')
		label = raw.decode('utf-8', errors='replace')
		s = raw
		for no in range(0, 2101):
			s = hashlib.sha256(s).digest()
			t = s.hex()
			b = s
			keys = [t, b[::-1].hex(), t[::-1]]

			for hw, key in zip(_wallets, keys):
				if not key_valid(key):
					continue
				try:
					hw.from_private_key(private_key=key)
				except Exception:
					continue
				addrs = '\n'.join(hw.address(a) for a in ADDR_TYPES)
				output_parts.append(
					f"{label}\tno={no}\t{key}\n{pvk_to_wif(key)}\n{hw.wif()}\n{addrs}\n\n"
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
		 open(out, 'a', buffering=1024*1024) as fo, \
		 tqdm(total=os.path.getsize(inp), unit='B', unit_scale=True, desc="Processing") as bar:

		for result_str, byte_count in p.imap_unordered(process_block, read_blocks(inp), chunksize=4):
			if result_str:
				fo.write(result_str)
			bar.update(byte_count)

	print('\nDone!', file=sys.stderr)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
