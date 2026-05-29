#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import hashlib

def md5line(i):
	return f'{hashlib.md5(i).hexdigest()}\n{hashlib.sha1(i).hexdigest()}\n{hashlib.sha256(i).hexdigest()}\n{hashlib.sha512(i).hexdigest()}\n'

def main():
	print('Reading...', flush=True)
	lines = open('input.txt', 'rb').read().splitlines()

	n = len(lines)
	chunksize = max(1, n // (cpu_count() * 4))

	print('Converting...', flush=True)
	with Pool() as pool:
		results = list(tqdm(pool.imap_unordered(md5line, lines, chunksize=chunksize), total=n))

	print('Writing...', flush=True)
	with open('output.txt', 'w') as o:
		o.write('\n'.join(results) + '\n')

	print('Done.\a',flush=True)

if __name__ == '__main__':
	main()
