#!/usr/bin/env python3

import os, sys
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

fn,ext=os.path.splitext(sys.argv[1])

print('Reading...', flush=True)
file=open(fn+ext,'r').read().splitlines()

a=open(fn+'.addrs'+ext,'w')
w=open(fn+'.wifs'+ext,'w')

print('Writing...', flush=True)

def go(i):
	c=i[0]
	if c=='1' or c=='3' or c=='b':
		a.write(i+'\n')
		a.flush()
	elif c=='5' or c=='K' or c=='L':
		w.write(i+'\n')
		w.flush()

process_map(go, file, max_workers=16, chunksize=1000)

print('\a',end='',file=sys.stderr)
