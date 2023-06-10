#!/usr/bin/env python3

# convert brainwallets to: privkey 0 # brainwallet # public address

from bitcoin import *
from tqdm.contrib.concurrent import process_map
import base58
import hashlib

i = open("input.txt","rb")
o = open("output.txt","wb")

c=0

for line in i:
	print(c,end='\r')
	x=line.strip()
	sha=hashlib.sha256(x).digest()
	tmp=b'\x80'+sha
	h=base58.b58encode_check(tmp)
	y=privtoaddr(sha)
	i=h + b" 0 # " + str.encode(y) + b' # ' + x
	#print(i.decode('utf-8'))
	o.write(i+b'\n')
	o.flush()
	c=c+1

i.close()
o.flush()
o.close()
