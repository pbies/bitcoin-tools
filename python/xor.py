#!/usr/bin/env python3

import sys
from tqdm import tqdm

print('Reading...', flush=True)
i=set(open('input.txt','r').read().splitlines())
o=open('output.txt','w')

x=2**256-1

print('Writing...', flush=True)
for j in tqdm(i):
	a=int(j,16)
	b=a^x
	d=hex(b)[2:].zfill(64)
	o.write(d+'\n')

print('\a', end='', file=sys.stderr)
