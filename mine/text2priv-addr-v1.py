#!/usr/bin/env python3

from bitcoin import *
from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" keys"):
		x=line.rstrip(b'\n')
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		privkey=base58.b58encode_check(tmp).decode('utf-8')
		addr=privtoaddr(privkey)
		wif=encode_privkey(privkey, 'wif')
		outfile.write(wif.encode('utf-8'))
		outfile.write(b';')
		outfile.write(str.encode(addr))
		outfile.write(b';')
		outfile.write(x)
		outfile.write(b'\n')

outfile.close()
