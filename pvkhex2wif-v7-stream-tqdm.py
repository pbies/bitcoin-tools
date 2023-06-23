#!/usr/bin/env python3

from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt):
		x=line.rstrip('\n')
		sha=bytes.fromhex(x)
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=bytes_to_str(h)+" 0 # "+x+'\n'
		outfile.write(i)

outfile.close()
