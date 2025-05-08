#!/usr/bin/env python3

import base58
import sys
from tqdm import tqdm

fn=sys.argv[1]

print('Reading...')
f=open(fn,'rb').read().splitlines()

o=open(fn+'.decoded','wb')

print('Writing...')
for i in tqdm(f):
	try:
		o.write(base58.b58decode_check(i)+b'\n')
	except:
		pass

print('\a', end='', file=sys.stderr)
