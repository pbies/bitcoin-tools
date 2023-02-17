#!/usr/bin/env python3

from bitcoin import *
from tqdm.contrib.concurrent import process_map
import base58

outfile = open("output.txt","w")

def worker(key):
	priv=base58.b58decode_check(key[:-1])[1:]
	pub=privtopub(priv)
	addr=pubtoaddr(pub)
	outfile.write(addr+'\n')

with open("input.txt","r") as f:
	process_map(worker, f.readlines(), max_workers=6, chunksize=20)
