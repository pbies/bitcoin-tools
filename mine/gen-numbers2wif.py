#!/usr/bin/env python3

import base58
import hashlib

outfile = open("output.txt","wb")

for i in range(0,2000001):
	x=str.encode(str(i))
	sha=hashlib.sha256(x).digest()
	tmp=b'\x80'+sha
	h=base58.b58encode_check(tmp)
	i=h+b" 0 # "+x+b'\n'
	outfile.write(i)

outfile.close()
