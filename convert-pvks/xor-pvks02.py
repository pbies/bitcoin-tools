#!/usr/bin/env python3
# Stream processing: read input line-by-line and show progress by input-file byte position.

from multiprocessing import Pool
from tqdm import tqdm
import os
import sys
import datetime
import time

infile_path = 'input.txt'
outfile_path = 'output.txt'
num_processes = 24

# Pool tuning
chunksize = 2000

g = 2**256
h = 2**256 - 1
i = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd036413f
j = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140
k = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def go(x: str) -> str:
	# x is a hex string (one per line)
	x = x.strip()
	if not x:
		return ""
	y = int(x, 16)
	a = hex(abs(g - y))[2:].zfill(64)
	b = hex(abs(h - y))[2:].zfill(64)
	c = hex(abs(i - y))[2:].zfill(64)
	d = hex(abs(j - y))[2:].zfill(64)
	e = hex(abs(k - y))[2:].zfill(64)
	return f'{x}\n{a}\n{b}\n{c}\n{d}\n{e}\n\n'

def iter_lines_with_byte_progress(path: str, pbar: tqdm):
	with open(path, 'rb') as f:
		for raw in f:
			# Progress by actual bytes consumed from the input file
			pbar.update(len(raw))
			line = raw.rstrip(b'\r\n')
			if not line:
				continue
			# Hex keys are ASCII; ignore unexpected bytes safely
			yield line.decode('ascii', errors='ignore')

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time = time.time()

	# Truncate output
	open(outfile_path, 'w', encoding='utf-8').close()

	in_size = os.path.getsize(infile_path)

	with tqdm(total=in_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
		with Pool(processes=num_processes) as pool:
			with open(outfile_path, 'a', encoding='utf-8', buffering=1024*1024) as outfile:
				for w in pool.imap_unordered(go, iter_lines_with_byte_progress(infile_path, pbar), chunksize=chunksize):
					if w:
						outfile.write(w)

	stop_time = time.time()
	print(start_msg)
	print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
