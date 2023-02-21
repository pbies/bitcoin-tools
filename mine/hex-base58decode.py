#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib
import binascii

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip('\n')
		y=binascii.unhexlify(x)
		try:
			h=base58.b58decode_check(y)
		except:
			outfile.write(y+b'\n')
			continue
		outfile.write(h+b'\n')

outfile.close()
