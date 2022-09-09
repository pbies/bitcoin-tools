#!/usr/bin/env python3

import base58
import hashlib
import sys
from tqdm import tqdm

outfile = open("output.txt","w")

with open("input.txt","r",encoding="utf-8") as f:
	content = f.readlines()

content = [x.rstrip('\n') for x in content]

for l in tqdm(content, total=len(content), unit=" lines"):
	line=l.rstrip('\n')
	a=line.encode('utf-8')
	b=hashlib.sha256(a).digest()
	f=b'\x80'+b
	g=base58.b58encode_check(f)
	h=g.decode('utf-8')+" 0 # "+line+"\n"
	outfile.write(h)

outfile.close()
