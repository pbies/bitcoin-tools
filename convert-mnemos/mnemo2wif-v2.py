#!/usr/bin/env python3

import binascii, hashlib, base58

with open("input.txt","r") as f:
	lines = f.readlines()

lines = [x.strip() for x in lines]

with open("output.txt","wb") as o:
	for line in lines:
		privWIF1 = hashlib.sha256(binascii.unhexlify('80'+line)).hexdigest()
		privWIF2 = hashlib.sha256(binascii.unhexlify(privWIF1)).hexdigest()
		privWIF3 = '80'+line+privWIF2[:8]
		WIF=base58.b58encode(privWIF3)
		#print(WIF)
		o.write(WIF+b'\n')
