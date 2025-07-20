#!/usr/bin/env python3

import sys, os, base58
from multiprocessing import Pool, Lock, Manager
from tqdm import tqdm

os.system('cls||clear')

i = open('input.txt','r').read().splitlines()
o = open('output.txt','w')

def go(x):
	y=base58.b58decode_check(x)
	z=y.hex()[2:]
	if len(z)==66:
		z=z[:-2]
	o.write(z+'\n')
	o.flush()

with Pool(processes=15) as pool:
	list(tqdm(pool.imap_unordered(go, i, chunksize=50)))

print('\a', end='', file=sys.stderr)
