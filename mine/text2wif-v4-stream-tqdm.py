#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import binascii
import bitcoin
import hashlib
import subprocess

outfile = open("output.txt","wb")

cnt=int(check_output(["wc", "-l", "input.txt"]).split()[0])

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		b=hashlib.sha256(x).digest()
		c=b.hex()
		d='80'+c
		g=bytes.fromhex(d)
		h=base58.b58encode_check(g)
		i=h+b" 0 # "+x+b'\n'
		outfile.write(i)

outfile.close()
