#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
import hashlib
import sys

def md5line(i):
	return hashlib.md5(i).hexdigest()

CHUNKSIZE = 2000

def main():
	with open('input.txt', 'rb') as f, open('output.txt', 'w') as o:
		lines = (line.rstrip(b'\r\n') for line in f)
		with Pool() as pool:
			for result in tqdm(pool.imap_unordered(md5line, lines, chunksize=CHUNKSIZE)):
				o.write(result + '\n')

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
