#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import hashlib

def md5line(i):
	return f'{hex(i)[2:].zfill(8)}\n'

def lines():
	for x in range(0,2**32):
		yield x

def main():
	n = 2**32
	chunksize = max(1, n // (cpu_count() * 4))

	print('Converting...', flush=True)
	with Pool() as pool, open('output.txt', 'w') as o:
		for line in tqdm(pool.imap_unordered(md5line, lines(), chunksize=chunksize), total=n):
			o.write(line)

	print('Done.\a', flush=True)

if __name__ == '__main__':
	main()
