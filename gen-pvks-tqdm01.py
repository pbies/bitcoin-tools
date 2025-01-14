#!/usr/bin/env python3

from tqdm import tqdm
import sys, os

if __name__ == '__main__':
	f = open('pvks.txt', 'a')
	for i in tqdm(range(0, int(sys.argv[1]))):
		pvk=os.urandom(32).hex()
		f.write(f'{pvk}\n')
		f.flush()
	print('\a', end='', file=sys.stderr)
