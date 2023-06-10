#!/usr/bin/env python3

import base58
import hashlib
import sys

with open("input.txt","rb") as f:
	content = f.readlines()

content = [x.strip() for x in content]

o = open('output.txt','wb')

for line in content:
	line=bytes(line)
	while len(line)<32:
		line=bytes([0])+line
	d=bytes([0])+line
	g=base58.b58encode_check(d)
	h=bytes(g,"utf-8")+bytes([32,48,32,35,32])+bytes(line)+bytes([10])
	o.write(h)
