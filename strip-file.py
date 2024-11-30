#!/usr/bin/env python3

import sys
from tqdm import tqdm

print('Reading...')
i=open(sys.argv[1],'r').read().splitlines()
o=open(sys.argv[1]+'.out','w')

print('Writing...')
for x in tqdm(i):
	y=x.strip()
	o.write(y+'\n')
	o.flush()

print('\a', end='', file=sys.stderr)
