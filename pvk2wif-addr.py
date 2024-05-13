#!/usr/bin/env python3

from tqdm import tqdm
import base58
import hashlib
from cryptos import *

cnt=sum(1 for line in open("input.txt", 'r'))

outfile = open("output.txt","w")

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt):
		pvk=line.rstrip('\n')
		sha=bytes.fromhex(pvk)
		tmp=b'\x80'+sha
		wif=base58.b58encode_check(tmp) # wif
		pub=privtopub(tmp)
		addr=pubtoaddr(pub)
		i=bytes_to_str(wif)+" 0 # "+pvk+' '+addr+'\n'
		outfile.write(i)

outfile.flush()
outfile.close()
