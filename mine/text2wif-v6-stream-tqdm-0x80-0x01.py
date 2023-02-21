#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import binascii
import bitcoin
import hashlib
import subprocess

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		b=hashlib.sha256(x).digest()
		d=b'\x80'+b+b'\x01'
		h=base58.b58encode_check(d)
		i=h+b" 0 # "+x+b'\n'
		outfile.write(i)

outfile.close()
