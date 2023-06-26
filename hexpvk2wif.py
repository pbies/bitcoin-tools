#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip('\n')
		#x='80'+x
		x=bytes.fromhex(x)
		h=base58.b58encode_check(x)
		outfile.write(h+b'\n')

outfile.close()
