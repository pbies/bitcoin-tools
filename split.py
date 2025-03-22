#!/usr/bin/env python3

import os, sys
from tqdm import tqdm

fn,ext=os.path.splitext(sys.argv[1])

print('Reading...', flush=True)
file=open(fn+ext,'r').read().splitlines()

a=open(fn+'.addrs'+ext,'w')
w=open(fn+'.wifs'+ext,'w')

print('Writing...', flush=True)

for i in tqdm(file):
	c=i[0]
	if c=='1' or c=='3' or c=='b':
		a.write(i+'\n')
		a.flush()
	elif c=='5' or c=='K' or c=='L':
		w.write(i+'\n')
		w.flush()

print('\a',end='',file=sys.stderr)
