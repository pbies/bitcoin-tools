#!/usr/bin/env python3

import sys, os
from tqdm import tqdm

print('Reading...', flush=True)
i=open(sys.argv[1], 'rb').read().splitlines()
o=open(sys.argv[1]+'.out', 'wb')

print('Writing...', flush=True)
for x in tqdm(i):
	y=x.strip()
	o.write(y+b'\n')
	o.flush()

os.rename(sys.argv[1]+'.out', sys.argv[1])

print('\a', end='', file=sys.stderr)
