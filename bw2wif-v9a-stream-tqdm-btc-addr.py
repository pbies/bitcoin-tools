#!/usr/bin/env python3

# brainwallets to WIFs with progress and original text as comment; also address

from cryptos import *
from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt):
		pwd=line.rstrip(b'\n')
		sha=hashlib.sha256(pwd).digest()
		tmp=b'\x80'+sha
		wif=base58.b58encode_check(tmp)
		pub=privtopub(tmp)
		addr=pubtoaddr(pub)
		i=wif+b' 0 # '+str.encode(addr)+b' '+bytearray(pwd)+b'\n'
		outfile.write(i)

outfile.close()
