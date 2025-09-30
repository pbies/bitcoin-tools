#!/usr/bin/env python3

from bitcoin import *
from tqdm.contrib.concurrent import process_map
import base58

outfile = open("output.txt","w")

def worker(key):
	try:
		priv=base58.b58decode_check(key[:-1])[1:]
	except:
		return
	addr=privtoaddr(priv)
	outfile.write(addr+' '+key)
	outfile.flush()

with open("input.txt","r") as f:
	process_map(worker, f.readlines(), max_workers=4, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
