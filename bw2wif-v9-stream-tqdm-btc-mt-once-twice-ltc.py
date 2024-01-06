#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
import os

i = open("input.txt","rb")
o = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

def go(x):
	x=x.rstrip(b'\n')
	sha=hashlib.sha256(x).digest()
	tmp=b'\xb0'+sha
	h=base58.b58encode_check(tmp)
	i=h+b" 0 # "+x+b'\n'
	o.write(i)
	sha2=hashlib.sha256(sha).digest()
	tmp=b'\xb0'+sha2
	h=base58.b58encode_check(tmp)
	i=h+b" 0 # "+x+b'\n'
	o.write(i)
	o.flush()
	return

process_map(go, i.readlines(), max_workers=4, chunksize=10000)
