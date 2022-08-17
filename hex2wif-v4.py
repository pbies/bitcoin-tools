#!/usr/bin/env python3
import bitcoin
import binascii
import base58
import hashlib

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","wb")
for x in content:
	ext=b'\x80'+binascii.unhexlify(x)
	wif=base58.b58encode_check(ext)
	print(wif)
	outfile.write(wif+b' 0\n')

outfile.close()
