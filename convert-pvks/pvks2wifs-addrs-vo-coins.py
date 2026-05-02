#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from libcrypto import Wallet
import os, sys

CHUNK_LINES = 10_000

def process_block(lines):
	out = []
	for line in lines:
		line = line.rstrip(b'\n').decode()
		try:
			wallet=Wallet(line)
		except Exception:
			continue
		p2pkh = wallet.get_address(coin="bitcoin", address_type="p2pkh")
		p2wsh = wallet.get_address(coin="bitcoin", address_type="p2sh-p2wpkh")
		p2wpkh = wallet.get_address(coin="bitcoin", address_type="p2wpkh")
		litecoin_address_p2pkh = wallet.get_address(coin="litecoin", address_type="p2pkh")
		litecoin_address_p2wsh = wallet.get_address(coin="litecoin", address_type="p2sh-p2wpkh")
		litecoin_address_p2wpkh = wallet.get_address(coin="litecoin", address_type="p2wpkh")
		out.append(
			line + "\n" +
			p2pkh + "\n" +
			p2wsh + "\n" +
			p2wpkh + "\n" +
			litecoin_address_p2pkh + "\n" +
			litecoin_address_p2wsh + "\n" +
			litecoin_address_p2wpkh + "\n" +
			"\n"
		)
	return ''.join(out)

def read_blocks(path):
	with open(path, 'rb', buffering=1024*1024) as f:
		block = []
		for line in f:
			block.append(line)
			if len(block) >= CHUNK_LINES:
				yield block
				block = []
		if block:
			yield block

def main():
	inp = 'input.txt'
	out = 'output.txt'

	with open(out, 'w'):
		pass

	workers = cpu_count()

	with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo:
		for result in p.imap_unordered(process_block, read_blocks(inp), chunksize=100):
			fo.write(result)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
