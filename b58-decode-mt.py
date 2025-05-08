#!/usr/bin/env python3

import base58
import sys
from tqdm import tqdm
from multiprocessing import Pool

fn=sys.argv[1]

print('Reading...', flush=True)
f=open(fn,'rb').read().splitlines()

o=open(fn+'.decoded','wb')

th=28
cnt = 10000

def go(x):
	try:
		o.write(base58.b58decode_check(x)+b'\n')
	except:
		return
	o.flush()

if __name__=='__main__':
	i=0
	print('Writing...', flush=True)
	with Pool(processes=th) as p, tqdm(f) as pbar:
		for result in p.imap_unordered(go, f, chunksize=1000):
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			i=i+1

print('\a', end='', file=sys.stderr)
