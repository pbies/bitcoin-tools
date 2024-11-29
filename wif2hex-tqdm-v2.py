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
		wif=line.rstrip('\n')
		hex=base58.b58decode_check(wif).hex()[2:66]
		outfile.write(hex+'\n')

outfile.close()
