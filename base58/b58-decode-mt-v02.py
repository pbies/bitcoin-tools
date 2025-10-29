#!/usr/bin/env python3

import base58
import sys
from tqdm import tqdm
from multiprocessing import Pool

def go(x):
	try:
		with open(outfile_path, 'a') as outfile:
			outfile.write(base58.b58decode_check(x).hex()[2:].zfill(64)+'\n')
	except:
		return

if __name__=='__main__':
	infile_path='input.txt'
	outfile_path='output.txt'
	print('Reading...', flush=True)
	f=set(open(infile_path,'r').read().splitlines())

	th=24
	cnt = 10000

	i=0
	open(outfile_path, 'w').close()
	print('Writing...', flush=True)
	with Pool(processes=th) as p, tqdm(f) as pbar:
		for result in p.imap_unordered(go, f, chunksize=1000):
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			i=i+1

print('\a', end='', file=sys.stderr)
