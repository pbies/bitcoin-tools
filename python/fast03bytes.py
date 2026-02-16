#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from bitcash import Key
import os, sys

CHUNK_LINES = 1000

def process_block(lines):
	out = []
	for line in lines:
		line = line.rstrip(b'\n')
		try:
			k = Key.from_hex(line.decode())
		except Exception:
			continue
		out.append(
			line.decode() + "\n" +
			k.to_wif() + "\n" +
			k.address[12:] + "\n\n"
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

	total_bytes = os.path.getsize(inp)
	processed_bytes = 0

	with open(out, 'w'):
		pass

	workers = cpu_count()

	with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo:
		for block, result in zip(
			read_blocks(inp),
			p.imap_unordered(process_block, read_blocks(inp), chunksize=100)
		):
			fo.write(result)
			processed_bytes += sum(len(line) for line in block)
			if processed_bytes > total_bytes:
				processed_bytes = total_bytes
			print(f'\r{processed_bytes:,}/{total_bytes:,}', end='', file=sys.stderr)

	print('\n\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
