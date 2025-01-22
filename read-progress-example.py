#!/usr/bin/env python3

import os
import sys
from tqdm import tqdm

print('Reading...', flush=True)
i=open('input.txt','r')
size=os.stat('input.txt').st_size

lines=[]
while True:
	l=i.readline().strip()
	if not l:
		break
	lines.append(l)
	pos=i.tell()
	perc=str(int(pos/size*100))
	print(perc+'%', end='\r')

print()
sys.exit(0)
o=open('output.txt','w')

x=2**256-1

print('Writing...', flush=True)
for j in tqdm(i):
	a=int(j,16)
	b=a^x
	c=hex(b)[2:]
	d='0'*(64-len(c))+c
	o.write(d+'\n')

print('\a', end='', file=sys.stderr)
