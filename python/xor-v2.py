#!/usr/bin/env python3

import sys
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

X = 2**256 - 1

def process_line(line: str) -> str:
	a = int(line, 16)
	return hex(a ^ X)[2:].zfill(64).encode()

input_path = 'input.txt'
output_path = 'output.txt'

file_size = os.path.getsize(input_path)

print('Processing...', flush=True)
with open(output_path, 'wb') as outfile:
	pass
with (
	open(input_path, 'rb') as infile,
	ThreadPoolExecutor(max_workers=os.cpu_count()) as executor,
	tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar,
):
	BATCH = 10_000
	batch = []
	last_pos = 0

	def flush_batch(b):
		futures = [executor.submit(process_line, line) for line in b]
		return [f.result() for f in futures]

	for raw in infile:
		line = raw.strip()
		if line:
			batch.append(line)

		if len(batch) >= BATCH:
			with open(output_path, 'ab') as outfile:
				for result in flush_batch(batch):
					outfile.write(result + b'\n')
			batch = []

		cur_pos = infile.tell()
		pbar.update(cur_pos - last_pos)
		last_pos = cur_pos

	if batch:
		with open(output_path, 'ab') as outfile:
			for result in flush_batch(batch):
				outfile.write(result + b'\n')

print('\a', end='', file=sys.stderr)
