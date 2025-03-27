#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time
import re

infile = open('input.txt','r')
good = open('good.txt','w')
bad = open('bad.txt','w')

def go(k):
	l=len(k)
	if l<32 or not re.search('^[0-9A-Fa-f]+$', k):
		bad.write(k+'\n')
		bad.flush()
		return
	if l==32:
		good.write(f'{k}\n')
		good.flush()
	if l>32:
		good.write(f'{k[:32]}\n{k[-32:]}\n')
		good.flush()

print('Reading...', flush=True)
lines = set(infile.read().splitlines())

print('Writing...', flush=True)
for line in tqdm(lines):
	go(line)

print('\a', end='', file=sys.stderr)
