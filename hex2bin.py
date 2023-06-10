#!/usr/bin/env python3
import bitcoin
import binascii
import base58

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","wb")
for x in content:
	outfile.write(base58.b58encode_check(binascii.unhexlify(x))+b' 0\n')

outfile.close()
