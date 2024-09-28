#!/usr/bin/env python3

import base58
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

i=open('input.txt','r').read().splitlines()
o=open('output.txt','wb')

def go(a):
	try:
		o.write(base58.b58encode_check(b'\xb0'+base58.b58decode_check(a)[2:])+b'\n')
	except:
		return

process_map(go, i, max_workers=8, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
