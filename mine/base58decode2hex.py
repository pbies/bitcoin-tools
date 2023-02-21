#!/usr/bin/env python3

# decode many base58check; progress bar

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		h=base58.b58decode_check(x)
		outfile.write(h.hex()+'\n')

outfile.close()
