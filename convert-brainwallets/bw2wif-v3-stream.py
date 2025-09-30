#!/usr/bin/env python3
import bitcoin
import binascii
import base58
import hashlib

outfile = open("output.txt","wb")

with open("input.txt","rb") as f:
	for line in f:
		x=line.rstrip(b'\n')
		b=hashlib.sha256(x).digest()
		c=b.hex()
		d='80'+c
		g=bytes.fromhex(d)
		h=base58.b58encode_check(g)
		i=h+b" 0 # "+x+b'\n'
		outfile.write(i)

outfile.close()
