#!/usr/bin/env python3

from tqdm import tqdm
import sys

def rev(a):
	return "".join(reversed([a[i:i+2] for i in range(0, len(a), 2)]))

print('Reading...')
i=open('input.txt','r').read().splitlines()
print('Writing...')
o=open('output.txt','w')

for line in tqdm(i):
	o.write(f'{rev(line)}\n')
	o.flush()

print('\a', end='', file=sys.stderr)
