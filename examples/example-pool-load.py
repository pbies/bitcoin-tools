#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58, re
import os, sys, hashlib

print('Reading...', flush=True)
lines = open('input.txt','r').read().splitlines()

print('Writing...', flush=True)
open('output.txt', 'w').close()

c=10000
t=0

def go(x):
	with open('output.txt','a') as outfile:
		outfile.write(x)

with Pool(processes=24) as p, tqdm(total=len(lines)) as pbar: # , unit='B', unit_scale=True
	for result in p.imap_unordered(go, lines, chunksize=1000):
		t=t+1
		if t==c:
			pbar.update(c)
			pbar.refresh()
			t=0

print('\a', end='', file=sys.stderr)
