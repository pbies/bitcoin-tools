#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import hashlib
import sys

def md5line(i):
	return hashlib.md5(i).hexdigest()

def main():
	lines = open('input.txt', 'rb').read().splitlines()

	with open('output.txt', 'w') as o:
		with Pool(processes=cpu_count()-2) as pool:
			for h in tqdm(pool.imap_unordered(md5line, lines), total=len(lines)):
				o.write(f'{h}\n')

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
