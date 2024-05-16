#!/usr/bin/env python3

from cryptos import *
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

def worker(line):
	bw=line.rstrip('\n')
	sha=hashlib.sha256(bw).digest()
	tmp=b'\x80'+sha
	wif=base58.b58encode_check(tmp) # wif
	addr=privtoaddr(sha)
	outfile.write(wif+b"\t"+addr+b'\n')
	outfile.flush()

infile=open("input.txt","rb")

outfile = open("output.txt","wb")

process_map(worker, infile.readlines(), max_workers=12, chunksize=10000)

infile.close()
outfile.flush()
outfile.close()

import sys
print('\a',end='',file=sys.stderr)
