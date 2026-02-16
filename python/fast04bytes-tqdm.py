#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from bitcash import Key
from tqdm import tqdm
import os

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

	with open(out, 'w'):
		pass

	workers = cpu_count()

	with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo, \
		tqdm(total=total_bytes, unit='B', unit_scale=True) as bar:

		for block, result in zip(
			read_blocks(inp),
			p.imap_unordered(process_block, read_blocks(inp), chunksize=100)
		):
			fo.write(result)
			bar.update(sum(len(line) for line in block))

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
