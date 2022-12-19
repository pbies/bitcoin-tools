#!/usr/bin/env python3

import base58
import hashlib
import sys
from tqdm import tqdm

outfile = open("output.txt","wb")

with open("input.txt","rb") as f:
	content = f.readlines()

content = [str(x).rstrip('\n') for x in content]

for l in tqdm(content, total=len(content), unit=" lines"):
	line=l.rstrip('\n')
	a=line.encode('utf-8')
	b=hashlib.sha256(a).digest()
	f=b'\x80'+b
	g=base58.b58encode_check(f)
	h=g+b" 0 # "+str.encode(line)+b"\n"
	outfile.write(h)

outfile.close()
