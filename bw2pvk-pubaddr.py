#!/usr/bin/env python3

# convert brainwallets to: privkey 0 # public address # brainwallet

from subprocess import check_output
from tqdm import tqdm
import base58
import ecdsa
import hashlib
from bitcoin import *

cnt=sum(1 for line in open("input.txt", 'rb'))

outfile = open("output.txt","wb")

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt):
		x=line.strip()
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		y=privtoaddr(sha)
		i=h+b" 0 # "+str.encode(y)+b' # '+x+b'\n'
		outfile.write(i)

outfile.close()
