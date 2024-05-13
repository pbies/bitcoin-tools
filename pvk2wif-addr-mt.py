#!/usr/bin/env python3

from cryptos import *
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

def worker(line):
	pvk=line.rstrip('\n')
	sha=bytes.fromhex(pvk)
	tmp=b'\x80'+sha
	wif=base58.b58encode_check(tmp) # wif
	pub=privtopub(tmp)
	addr=pubtoaddr(pub)
	i=bytes_to_str(wif)+" 0 # "+pvk+' '+addr+'\n'
	outfile.write(i)

cnt=sum(1 for line in open("input.txt", 'r'))

infile=open("input.txt","r")

outfile = open("output.txt","w")

process_map(worker, infile.readlines(), max_workers=6, chunksize=10000)

infile.close()
outfile.flush()
outfile.close()

import sys
print('\a',end='',file=sys.stderr)
