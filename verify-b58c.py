#!/usr/bin/env python3

import base58
import hashlib
import sys
from tqdm import tqdm

i = open("wifs.txt","r")
o = open("wifs-ok.txt","w")

cnt=sum(1 for line in i)

i.seek(0,0)

for j in tqdm(i,total=cnt):
	j=j.strip()
	try:
		x=base58.b58decode_check(j)
	except:
		continue
	o.write(base58.b58encode_check(x).decode('cp437')+"\n")
