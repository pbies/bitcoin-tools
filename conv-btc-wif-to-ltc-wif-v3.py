#!/usr/bin/env python3

import base58
from tqdm import tqdm

with open('input.txt','r') as i:
	with open('output.txt','wb') as o:
		cnt=sum(1 for line in open("input.txt", 'r'))
		for l in tqdm(i, total=cnt):
			l=l.strip('\n')
			a=base58.b58encode_check(b'\xb0'+base58.b58decode_check(l)[2:])+b'\n'
			o.write(a)
