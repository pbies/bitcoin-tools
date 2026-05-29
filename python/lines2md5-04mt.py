#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import hashlib
import sys

def md5line(i):
	return hashlib.md5(i).hexdigest()

def main():
	lines = open('input.txt', 'rb').read().splitlines()

	n = len(lines)
	chunksize = max(1, n // (cpu_count() * 4))

	with Pool() as pool:
		results = list(tqdm(pool.imap_unordered(md5line, lines, chunksize=chunksize), total=n))

	with open('output.txt', 'w') as o:
		o.write('\n'.join(results) + '\n')

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
