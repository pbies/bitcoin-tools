#!/usr/bin/env python3

from tqdm import tqdm
import base58

cnt=sum(1 for line in open("input.txt", 'r'))

o = open("output.txt","wb")

with open("input.txt","rb") as i:
	for line in tqdm(i, total=cnt):
		d=line.strip()
		o.write(base58.b58decode_check(d)+b'\n')
