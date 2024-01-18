#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("tmp2.txt", 'r'))

with open("tmp2.txt","r") as f:
	for line in tqdm(f, total=cnt):
		x=line.rstrip('\n')
		y=bytes.fromhex(x)
		sha=hashlib.sha256(y).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=h+b' 0\n'
		outfile.write(i)

outfile.flush()
outfile.close()
