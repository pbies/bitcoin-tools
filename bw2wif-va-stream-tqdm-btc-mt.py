#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
import os

i = open("input.txt","rb").read().splitlines()
o = open("output.txt","wb")

def go(x):
	sha=hashlib.sha256(x).digest()
	tmp=b'\x80'+sha
	h=base58.b58encode_check(tmp)
	i=h+b" 0 # "+x+b'\n'
	o.write(i)
	o.flush()

process_map(go, i, max_workers=20, chunksize=10000)
