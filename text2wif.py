#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("input.txt","r",encoding="utf-8") as f:
	content = f.readlines()

content = [x.rstrip() for x in content]

o = open('output.txt','w',encoding="utf-8")

for line in content:
	a=line.encode('utf-8')
	b=hashlib.sha256(a).digest()
	c=b.hex()
	d='80'+c
	f=bytes.fromhex(d)
	g=base58.b58encode_check(f)
	h=g.decode('utf-8')+" 0 # "+line+"\n"
	o.write(h)
