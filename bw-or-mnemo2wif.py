#!/usr/bin/env python3

import base58
import hashlib
from tqdm import tqdm

o = open('output.txt','wb')
cnt=sum(1 for line in open("input.txt", 'r'))

for i in tqdm(open('input.txt','rb'),total=cnt):
	i=i.strip()
	sha = hashlib.sha256(i).digest()
	#sha.update(i).digest()
	#rip = hashlib.new('ripemd160')
	#rip.update(sha)
	#rip=rip.digest()
	o1=b'\x80'+sha
	wif1=base58.b58encode_check(o1)+b' 0\n'
	o.write(wif1)
	#o2=b'\x80'+rip
	#wif2=base58.b58encode_check(o2)+b' 0\n'
	#o.write(wif2)

o.flush()
o.close()
