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

def count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def main():
	inp = 'input.txt'
	out = 'output.txt'

	total_lines = count_lines(inp)
	processed = 0

	with open(out, 'w'):
		pass

	workers = cpu_count()

	with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo:
		for block, result in zip(read_blocks(inp),
			p.imap_unordered(process_block, read_blocks(inp), chunksize=100)):
			fo.write(result)
			processed += len(block)
			if processed > total_lines:
				processed = total_lines
			print(f'\r{processed:,}/{total_lines:,}', end='', file=sys.stderr)

	print('\n\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
