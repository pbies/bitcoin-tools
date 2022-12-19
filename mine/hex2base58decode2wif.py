#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib
import binascii

outfile = open("output.txt","wb")

cnt=int(check_output(["wc", "-l", "input.txt"]).split()[0])

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		y=binascii.unhexlify(x)
		sha=hashlib.sha256(y).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=h+b' 0 # hex: '+x+b' wif: '+y+b'\n'
		outfile.write(i)

outfile.close()
