#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('hex-once.txt','wb')

for line in content:
	a=bytearray.fromhex(line)
	b=hashlib.sha256(a).digest()
	c=b.hex()
	d='80'+c
	f=bytes.fromhex(d)
	g=base58.b58encode_check(f)
	h=g+b" 0\n"
	o.write(h)
