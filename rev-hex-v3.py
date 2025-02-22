#!/usr/bin/env python3

import sys, os
from tqdm import tqdm

i = open('input.txt','r').read().splitlines()
o = open('output.txt','w')

for line in tqdm(i):
	h1=line[::-1]
	try:
		h2=bytes.fromhex(line)
	except:
		continue
	h2=h2[::-1]
	h2=h2.hex()
	o.write(f'{line}\n{h1}\n{h2}\n')
	o.flush()

print('\a', end='', file=sys.stderr)
