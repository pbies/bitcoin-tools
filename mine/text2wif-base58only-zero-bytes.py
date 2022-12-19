#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('output.txt','w')

for line in content:
	a=bytes(line,'utf-8')
	if len(a)>32: continue
	while len(a) < 32:
		a=bytes([0])+a
	b=a
	#print(b)
	c=b.hex()
	d='80'+c
	f=bytes.fromhex(d)
	g=base58.b58encode_check(f)
	h=g+" 0\n"
	o.write(h)

# sort -u output.txt > import.txt
