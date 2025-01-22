#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time
import base58

infile = open('addrs.txt','r')
good = open('addrs-good.txt','w')
bad = open('addr-bad.txt','w')

def go(k):
	try:
		x=base58.b58decode_check(k)
	except:
		bad.write(k+'\n')
		bad.flush()
		return
	good.write(k+'\n')
	good.flush()

print('Reading...', flush=True)
lines = infile.read().splitlines()
lines = [x.strip() for x in lines]

print('Writing...', flush=True)
process_map(go, lines, max_workers=6, chunksize=1000, ascii=False)

print('\a', end='', file=sys.stderr)
