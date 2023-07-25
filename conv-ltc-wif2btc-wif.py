#!/usr/bin/env python3

from tqdm import tqdm
import base58

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt):
		wif=line.rstrip('\n')
		tmp=base58.b58decode_check(wif)[1:]
		tmp=b'\xb0'+tmp
		wif=base58.b58encode_check(tmp)
		outfile.write(wif+b'\n')

outfile.close()
