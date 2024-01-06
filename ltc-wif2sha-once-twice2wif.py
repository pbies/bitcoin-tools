#!/usr/bin/env python3

import hashlib
import base58
import binascii
from tqdm import tqdm

cnt=sum(1 for line in open("input.txt", 'r'))

with open('output.txt','w') as o:
	for i in tqdm(open('input.txt','r'),total=cnt):
		private_key_WIF = i.strip()
		first_encode = base58.b58decode_check(private_key_WIF)
		s1=hashlib.sha256(first_encode).digest()
		s2=hashlib.sha256(s1).digest()
		r1=base58.b58encode_check(b'\xb0'+s1)
		r2=base58.b58encode_check(b'\xb0'+s2)
		o.write(f'{r1.decode()} 0\n')
		o.write(f'{r2.decode()} 0\n')
