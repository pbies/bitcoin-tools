#!/usr/bin/env python3

from bitcoin import *
from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		pub=privtopub(tmp)
		addr=pubtoaddr(pub)
		i=h + b":" + str.encode(addr) + b":" + x + b"\n"
		outfile.write(i)

outfile.close()
